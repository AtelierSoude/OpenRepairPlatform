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

// Overloading findIndex for dates
Array.prototype.findDate = function(date) {
    return this.findIndex(function(x) {
        return x.sameDay(date);
    });
}

Array.prototype.insert_sorted_date = function(date) {
    if(this.length == 0){
        this.push([date_ident, date]);
        return -2;
    }

    for (var i = 0; i < this.length; i++){
        if(this[i][1].sameDay(date))
            return -1;
        // we can assert this since following day as there are no duplicates
        if (this[i][1].valueOf() > date.valueOf()){
            this.splice(i, 0, [date_ident, date]);
            return this[i+1][0]; // return class of previous element
        }
    }

    this.push([date_ident, date]);
    return this.length;

}

Array.prototype.findDate_2D = function(date) {
    var i = 0;
    var ident = parseInt(ident);
    for (i = 0; i < this.length; i++)
        if(this[i][1].sameDay(date))
            return i;
    return -1;
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



var date_ident = 0;
var all_dates = [];

function delete_event_button(x){
    ident = x.target.id.replace(/delete-event-/g, '');
    document.getElementById("event-"+ident).remove();
    document.getElementById("delete-event-" + ident).remove();
    document.getElementById("br-event-" + ident).remove();

    var index = all_dates.ident_indexOf(ident);
    console.log(ident);
    if (index != -1)
        all_dates.splice(index, 1);
}

function add_event_to_dom(event, date_div, place=-1){
    var span_event = document.createElement("span");
    span_event.classList.add("event");
    span_event.id= "event-" + event[0];

    let date_string = "" + event[1].toLocaleDateString() + " ";
    let text_node = document.createTextNode(date_string);
    let br = document.createElement("br");
    br.id = "br-event-" + event[0];

    var btn = document.createElement("input");
    btn.type = "button";
    btn.value = "-";
    btn.class = "delete-event";
    btn.id = "delete-event-" + event[0];


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
    if (all_dates.findDate_2D(date) != -1)
        return;
    all_dates.push([date_ident, date]);
    date_ident++;
}

function sort_dates(){
    all_dates.sort(function(a, b){
        if (a[1] < b[1]) return -1;
        if (a[1] > b[1]) return 1;
        return 0;
    });
    for (var i = 0; i < all_dates.length; i++)
        all_dates[i][0] = i;

    date_ident = all_dates.length;
}

function stage_two(dates){
    var date_div = document.querySelector("#date-list");
    dates.forEach(function (date) {add_event(date)});
    sort_dates();
    document.getElementById("date-list").innerHTML = "";
    all_dates.forEach(function (event) {add_event_to_dom(event, date_div)});
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
    ident = x.target.id.replace(/delete-interval-/g, '');
    document.getElementById("interval-"+ident).remove();
    document.getElementById("delete-interval-" + ident).remove();
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

document.getElementById("new-interval").onclick = function(){
    last = document.querySelector("span.interval:last-of-type");
    ident = last.id.replace(/interval-/g, '');

    if(!document.getElementById('delete-interval-' + ident)){
        var btn = document.createElement("input");
        btn.type = "button";
        btn.value = "-";
        btn.class = "delete-interval";
        btn.id = "delete-interval-" + ident;
        document.querySelector('span.intervals').appendChild(btn);
    }

    var input_begin = document.createElement("input");
    input_begin.type = "date";
    input_begin.classList.add("begin");

    var input_end = document.createElement("input");
    input_end.type = "date";
    input_end.classList.add("end");

    var span_interval = document.createElement("span");
    span_interval.classList.add("interval");
    span_interval.id= "interval-" + interval;

    let br = document.createElement("br");

    span_interval.appendChild(br);

    span_interval.innerHTML += "du "
    span_interval.appendChild(input_begin);
    span_interval.innerHTML += " au "
    span_interval.appendChild(input_end);


    document.querySelector('span.intervals').appendChild(span_interval);

    refresh_buttons();
    interval++;
};

document.getElementById("new-event").onclick = function(){
    var new_date_string = document.getElementById("new-event-date").value;
    if (new_date_string == '')
        return;

    var new_date = new Date(new_date_string);
    var index = all_dates.insert_sorted_date(new_date);
    var date_div = document.querySelector("#date-list");
    if (index == -1)
        return;

    console.log(index);
    add_event_to_dom([date_ident, new_date], date_div, index);

    date_ident++;
};

document.getElementById("id_organization").onchange = function(x){
    let payload = {
        organization_id: x.target.value
    }
    var formBody = payload_to_formBody(payload);
    fetch('/api/getPlacesForOrganization/', {
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        method: "POST",
        body: formBody
    })
        .then(handleErrors)
        .then(function(res){ return res.json(); })
        .then(function(data){
            var place_sel = document.getElementById("id_location");
            places = data['places'];

            // Clear locations selection
            for (var i = 0; i < place_sel.length; i++)
                place_sel.remove(i);

            for ( key in places ) {
                option = document.createElement( 'option' );
                option.value = key;
                option.text = places[key];
                place_sel.add( option );
            }
        });
}

function to_seconds(string){
    tt=string.split(":");
    sec=tt[0]*3600+tt[1]*60;
    return sec;
}

function on_submit(){
    var data = document.getElementById("submit-data");
    var actual_start = document.getElementById("start-time");
    var actual_end = document.getElementById("end-time");
    var actual_countdown = document.getElementById("publish-countdown");

    var hidden_start = document.getElementById("id_starts_at");
    var hidden_end = document.getElementById("id_ends_at");
    var hidden_countdown  = document.getElementById("id_publish_at");
    if(all_dates.length == 0){
        alert("temp warning Put in form valid that no dates were sent");
    }
    else{
        var dates_timestamps = [];
        all_dates.forEach(function(date){
            //js timestamps are in milliseconds but epoch is in seconds
            let unix_time = date[1].valueOf() / 1000;
            dates_timestamps.push(unix_time);
        });
        data.value = JSON.stringify(dates_timestamps);
        //parse int for timestamp addition
        hidden_start.value = to_seconds(actual_start.value);
        hidden_end.value = to_seconds(actual_end.value);
        hidden_countdown.value = actual_countdown.value;

        // wrap around next day if end time is before start
        if (hidden_end.value < hidden_start.value)
            hidden_end.value = hidden_end.value*1 + 3600*24;

        data.form.submit();
    }
}
