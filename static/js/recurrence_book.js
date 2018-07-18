function parse_dates(){
    up_until = document.getElementById('up_until').value;

    //Set now to midnight
    now = new Date();

    //Set until to midnight + 1 day, for last day inclusion rule
    until = new Date(up_until);
    until.setDate(until.getDate() + 1);

    return {
        'now': now,
        'until': until,
    };
}

// Overload of ISO string removing milliseconds in accordance to RRule's RFC
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString

function pad(number) {
    if ( number < 10 ) {
        return '0' + number;
    }
    return number;
}

Date.prototype.sameDay = function(d) {
    return this.getFullYear() === d.getFullYear()
        && this.getDate() === d.getDate()
        && this.getMonth() === d.getMonth();
}

Date.prototype.toRRString = function() {
    return this.getUTCFullYear()
        + pad( this.getUTCMonth() + 1 )
        + pad( this.getUTCDate() )
        + 'T'
        + pad( this.getUTCHours() )
        + pad( this.getUTCMinutes() )
        + pad( this.getUTCSeconds() )
        + 'Z';
};

// TODO: test this
Array.prototype.insert_sorted_date = function(date) {
    if(this.length == 0){
        this.push(date);
    }

    for (var i = 0; i < this.length; i++)
        if (this[i]['js_date'].valueOf() > date['js_date'].valueOf())
            this.splice(i, 0, [date_ident, date]);

    this.push(date);
}

function findDate(set, date){
    return_keys = [];
    Object.entries(set).forEach(function([key, value]){
        if(value['js_date'].sameDay(date))
            return_keys.push(parseInt(key));
    });
    return return_keys;
}

Array.prototype.ident_indexOf = function(ident){
    var i = 0;
    var ident = parseInt(ident);
    for (i = 0; i < this.length; i++)
        if(this[i][0] == ident)
            return i;
    return -1;
}

function RRule_format(date){
    let ret = date.toISOString();
    ret = ret.replace(/-/g, '');
    ret = ret.replace(/:/g, '');
    ret = ret.replace(/\./g, '');

    return ret;
}

function apply_exclusions(rules){
    intervals = [];
    intervals_html = document.querySelectorAll('span.interval');
    intervals_html.forEach(function(interval){
        begin = interval.querySelector('.begin').value;
        end = interval.querySelector('.end').value;
        if (begin != '' && end != ''){
            intervals.push([begin, end])
        }
    });

    var all_dates = rules.all();

    intervals.forEach(function(interval){
        //Set interval_end to midnight + 1 day, for last day inclusion rule
        interval_end = new Date(interval[1]);
        interval_end.setDate(interval_end.getDate() + 1);
        excluded_dates = rules.between(new Date(interval[0]), interval_end);

        excluded_dates.forEach(function(date){
            var index = all_dates.findDate(date);
            if (index != -1)
                all_dates.splice(index, 1);
        });
    });

    return all_dates;
}

function on_weekly(){
    checked_weekdays = document.querySelectorAll('input[name=weekday]:checked');
    checked_weekdays = [...checked_weekdays].map(function(weekday){
        return parseInt(weekday.value);
    });

    dates = parse_dates();
    now = dates.now;
    until = dates.until;

    if (up_until != ''){
        var rule = new RRule({
            freq: RRule.WEEKLY,
            interval: 1,
            byweekday: checked_weekdays,
            dtstart: now,
            until: until,
        });
        return apply_exclusions(rule);
    }
}

function on_monthly(){
    var nth = document.getElementById("nth").value;
    var day = document.getElementById("day").value;
    var count = document.getElementById("event-count-monthly").value;

    dates = parse_dates();
    now = dates.now;
    until = dates.until;
    var rule_str = "FREQ=MONTHLY;BYDAY=" + nth + day +
        ";COUNT=" + count +
        ";DTSTART=" + now.toRRString() ;

    var rule = rrulestr(rule_str);
    return apply_exclusions(rule);
}

function on_yearly (){
    var day_of_month = document.getElementById("day-of-month").value;
    var month = document.getElementById("month").value;
    var count = document.getElementById("event-count-yearly").value;
    dates = parse_dates();
    now = dates.now;
    until = dates.until;

    var rule = new RRule({
        freq: RRule.YEARLY,
        dtstart: now,
        count: parseInt(count),
        bymonth: parseInt(month),
        bymonthday: parseInt(day_of_month),
    });
    return apply_exclusions(rule);
}

function stage_one(){
    checked_type = document.querySelector('input[name="repeat"]:checked').value;
    dates = {}
    dates = function(checked_type){
        if (checked_type === "weekly")
            return on_weekly();
        else if (checked_type === "monthly")
            return on_monthly();
        else
            return on_yearly();
    }(checked_type);

    stage_two(dates);
}

function delete_event_button(x){
    ident = x.target.id.replace(/delete-event-/g, '');
    document.getElementById("event-"+ident).remove();
    document.getElementById("delete-event-" + ident).remove();
    document.getElementById("br-event-" + ident).remove();

    var index = all_dates.ident_indexOf(ident);
    if (index != -1)
        all_dates.splice(index, 1);
}

function add_event_to_dom(event, date_div, place=-1){
    console.log(event);
    id = event['id']
    var span_event = document.createElement("span");
    span_event.classList.add("event");
    span_event.id= "event-" + id;

    let date_string = event['title'] + " le " + event['formatted_date'];
    let text_node = document.createTextNode(date_string);
    let br = document.createElement("br");
    br.id = "br-event-" + id;

    var btn = document.createElement("input");
    btn.type = "button";
    btn.value = "-";
    btn.class = "delete-event";
    btn.id = "delete-event-" + id;


    btn.onclick = function (x) {
        delete_event_button(x);
    }

    span_event.appendChild(text_node);
    // default behaviour or no prior date when adding punctual date
    if (place == -1 || place == -2){
        date_div.appendChild(span_event);
        date_div.appendChild(btn);
        date_div.appendChild(br);
    }
    else{
        var before_node = document.getElementById("event-" + place);
        date_div.insertBefore(span_event, before_node);
        date_div.insertBefore(btn, before_node );
        date_div.insertBefore(br, before_node);
    }
}

function add_event(date){
    // Don't add the date if already in list of dates
    // Or if it is already in selected dates
    dates = findDate(unselected_dates, date);
    dates.forEach(function(date){
        unselected_dates[date]['id'] = date;
        selected_dates.insert_sorted_date(unselected_dates[date]);
        delete unselected_dates[date];
        date_ident++;
    });
}

function stage_two(dates){
    var date_div = document.querySelector("#date-list");
    dates.forEach(function (date) {add_event(date)});
    document.getElementById("date-list").innerHTML = "";
    selected_dates.forEach(function (event) {add_event_to_dom(event, date_div)});
}

function reset_list(){
    document.getElementById("date-list").innerHTML = "";
    all_dates = [];
    date_ident = 0;
}


document.getElementById("generate").onclick = function() {
    reset_list();
    stage_one();
};

document.getElementById("append").onclick = function() {
    stage_one();
    // stage_two();
}
document.getElementById("reset").onclick = reset_list;

var interval = 1;

function delete_interval_button(x){
    console.log(selected_dates);
    ident = x.target.id.replace(/delete-interval-/g, '');
    document.getElementById("interval-"+ident).remove();
    document.getElementById("delete-interval-" + ident).remove();

    unselected_dates[ident] = all_dates[date];
    delete selected_dates[date];
    console.log(selected_dates);
    refresh_buttons();
}

function refresh_buttons(){
    intervals = document.querySelectorAll('span.interval');
    last = document.querySelector("span.interval:last-of-type");
    intervals.forEach(function(interval){
        // only keep the value of the ident part
        ident = interval.id.replace(/interval-/g, '');
        if (interval !== last){
            document.getElementById("delete-interval-" + ident).onclick = function(x){
                delete_interval_button(x);
            }
        }
    });
}

// document.getElementById("new-interval").onclick = function(){
//     last = document.querySelector("span.interval:last-of-type");
//     ident = last.id.replace(/interval-/g, '');

//     if(!document.getElementById('delete-interval-' + ident)){
//         var btn = document.createElement("input");
//         btn.type = "button";
//         btn.value = "-";
//         btn.class = "delete-interval";
//         btn.id = "delete-interval-" + ident;
//         document.querySelector('span.intervals').appendChild(btn);
//     }

//     var input_begin = document.createElement("input");
//     input_begin.type = "date";
//     input_begin.classList.add("begin");

//     var input_end = document.createElement("input");
//     input_end.type = "date";
//     input_end.classList.add("end");

//     var span_interval = document.createElement("span");
//     span_interval.classList.add("interval");
//     span_interval.id= "interval-" + interval;

//     let br = document.createElement("br");

//     span_interval.appendChild(br);

//     span_interval.innerHTML += "du "
//     span_interval.appendChild(input_begin);
//     span_interval.innerHTML += " au "
//     span_interval.appendChild(input_end);


//     document.querySelector('span.intervals').appendChild(span_interval);

//     refresh_buttons();
//     interval++;
// };

function on_submit(){
    var data = document.getElementById("submit-data");

    if(selected_dates.length == 0){
        alert("temp warning Put in form valid that no dates were sent");
    }
    else{
        var events_pk = [];
        selected_dates.forEach(function(date){
            events_pk.push(date['id']);
        });
        console.log(events_pk);
        data.value = JSON.stringify(events_pk);
        data.form.submit();
    }
}

function get_organizations(){
    let csrftoken = getCookie('csrftoken');
    let headers = new Headers();
    headers.append('X-CSRFToken', csrftoken);

    fetch('/api/getOrganizations/', {
        headers: headers,
        method: "POST",
        credentials: 'include',
    })
        .then(handleErrors)
        .then(function(res){ return res.json(); })
        .then(function(data){
            let organizations = data['organizations'];
            let select_organization = document.getElementById("organization");
            Object.entries(organizations).forEach(function([key, value]){
                let option = document.createElement("option");
                option.value = key;
                option.innerHTML = value;
                select_organization.appendChild(option);
            });

            // Force change event for accurate handling of the first organization
            var event = new Event('change');
            select_organization.dispatchEvent(event);
        });
}

function get_dates_callback(data){
    unselected_dates = data['dates'];
    Object.entries(unselected_dates).forEach(function([key, value]){
        value['js_date'] = new Date(value['timestamp'] * 1000);
    });
    all_dates = unselected_dates;
}

function get_dates(pk){
    let csrftoken = getCookie('csrftoken');
    let headers = new Headers();
    headers.append('X-CSRFToken', csrftoken);
    headers.append('Content-Type', 'application/x-ww-form-urlencoded; charset=UTF-8');

    let payload = {
        organization_pk: pk,
    }
    let formData = payload_to_formBody(payload);
    var ret = {}

    fetch('/api/getDates/', {
        headers: headers,
        method: "POST",
        body: formData,
        credentials: 'include',
    })
        .then(handleErrors)
        .then(function(res){ return res.json(); })
        .then(function(data){
            get_dates_callback(data);
        });
}

get_organizations();
var all_dates = {}
var unselected_dates = {}
var selected_dates = [];
var date_ident = 0;

document.getElementById("organization").onchange = function(){
    get_dates(this.value);
}
