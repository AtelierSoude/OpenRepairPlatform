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
        console.log("i");
        console.log(interval);

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
    console.log(all_dates);


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

function stage_two(dates){
    console.log(dates);
}


document.getElementById("generate").onclick = function() {
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
};

var interval = 1;

function delete_button(x){
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
                delete_button(x);
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
