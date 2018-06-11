function parse_dates(){
    up_until = document.getElementById('up_until').value;

    //Set now to midnight
    now = new Date();
    now = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1, 0, 0, 0, 0);

    //Set until to midnight + 1 day, for last day inclusion rule
    until = new Date(up_until);
    until.setDate(until.getDate() + 1);

    return {
        'now': now,
        'until': until,
    };
}

// Polyfill of ISO string removing milliseconds in accordance to RRule's RFC
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString

function pad(number) {
    if ( number < 10 ) {
        return '0' + number;
    }
    return number;
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
            var index = all_dates.findIndex(function(x) {
                return x.valueOf() === date.valueOf();
            });

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
    // refresh_buttons();
}

var date_ident = 0;

function stage_two(dates){
    date_list = document.querySelector("#date-list");

    dates.forEach(function(date){
        var span_event = document.createElement("span");
        span_event.classList.add("event");
        span_event.id= "event-" + date_ident;

        let date_string = "Le " + date.toLocaleDateString() + " ";
        let text_node = document.createTextNode(date_string);
        let br = document.createElement("br");
        br.id = "br-event-" + date_ident;

        var btn = document.createElement("input");
        btn.type = "button";
        btn.value = "-";
        btn.class = "delete-event";
        btn.id = "delete-event-" + date_ident;

        btn.onclick = function (x) {
            delete_event_button(x);
        }

        span_event.appendChild(text_node);
        date_list.appendChild(span_event);
        date_list.appendChild(btn);
        date_list.appendChild(br);
        date_ident++;
    });
}

function reset_list(){
    document.getElementById("date-list").innerHTML = "";
}


document.getElementById("generate").onclick = function() {
    reset_list();
    stage_one();
};

document.getElementById("append").onclick = stage_one;
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
    //     `<br>
    //     <span class="interval" id="interval-${interval}">
    //     du <input class="begin" type="date">
    //     au <input class="end" type="date">
    //     </span>`

    refresh_buttons();
    interval++;

};
