let french = {
    firstDayOfWeek: 1,
    weekdays: {
        shorthand: ["dim", "lun", "mar", "mer", "jeu", "ven", "sam"],
        longhand: [
            "dimanche",
            "lundi",
            "mardi",
            "mercredi",
            "jeudi",
            "vendredi",
            "samedi",
        ]
    },
    months: {
        shorthand: [
            "janv",
            "févr",
            "mars",
            "avr",
            "mai",
            "juin",
            "juil",
            "août",
            "sept",
            "oct",
            "nov",
            "déc",
        ],
        longhand: [
            "janvier",
            "février",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
        ]
    },
    ordinal: function (nth) {
        if (nth > 1)
            return "";
        return "er";
    },
    rangeSeparator: " au ",
    weekAbbreviation: "Sem",
    scrollTitle: "Défiler pour augmenter la valeur",
    toggleTitle: "Cliquer pour basculer"
};

// Django datetime field looks like this: 2019-05-23 16:43:16
let dateTimeOpts = {
    enableTime: true,
    dateFormat: "Y-m-d H:i:s",
    altInput: true,
    locale: french,
    altFormat: "j F - H\\hi",
    time_24hr: true,
};

flatpickr("#id_publish_at", dateTimeOpts);
