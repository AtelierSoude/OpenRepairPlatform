from django_assets import Bundle, register

# SCSS

scss_custom_bootstrap = Bundle(
    "scss/custom_bootstrap.scss",
    filters="scss",
    output="css/custom_bootstrap.css",
)
scss_openrepairplatform = Bundle(
    "scss/openrepairplatform.scss", filters="scss", output="css/openrepairplatform.css"
)
scss_places = Bundle(
    "scss/lib/leaflet.scss",
    "scss/places/leaflet_custom.scss",
    "scss/places/custom.scss",
    filters="scss",
    output="css/leaflet_custom.css",
)
scss_detail_place = Bundle(
    "scss/lib/leaflet.scss",
    "scss/places/leaflet_custom.scss",
    filters="scss",
    output="css/detail_place.css",
)
scss_auto_complete = Bundle(
    "scss/lib/auto-complete.scss",
    filters="scss",
    output="css/auto-complete.css",
)
scss_detail_event = Bundle(
    "scss/lib/auto-complete.scss",
    "scss/lib/leaflet.scss",
    filters="scss",
    output="css/detail_event.css",
)
scss_detail_user = Bundle(
    "scss/user/detail.scss",
    filters="scss",
    output="css/detail_user.css",
)
scss_create_edit_event = Bundle(
    "scss/lib/flatpickr.scss",
    filters="scss",
    output="css/create_edit_event.css",
)
scss_detail_organization = Bundle(
    "scss/lib/auto-complete.scss",
    filters="scss",
    output="css/detail_organization.css",
)

# CSS minify
css_custom_bootstrap = Bundle(
    scss_custom_bootstrap,
    filters="cssrewrite,cssmin",
    output="css/custom_bootstrap.min.css",
)
css_openrepairplatform = Bundle(
    scss_openrepairplatform,
    filters="cssrewrite,cssmin",
    output="css/openrepairplatform.min.css",
)
css_places = Bundle(
    scss_places, filters="cssrewrite,cssmin", output="css/places.min.css"
)
css_detail_place = Bundle(
    scss_detail_place,
    filters="cssrewrite,cssmin",
    output="css/detail_place.min.css",
)
css_auto_complete = Bundle(
    scss_auto_complete,
    filters="cssrewrite,cssmin",
    output="css/auto-complete.min.css",
)
css_detail_event = Bundle(
    scss_detail_event,
    filters="cssrewrite,cssmin",
    output="css/detail_event.min.css",
)
css_detail_user = Bundle(
    scss_detail_user,
    filters="cssrewrite,cssmin",
    output="css/detail_user.min.css",
)
css_create_edit_event = Bundle(
    scss_create_edit_event,
    filters="cssrewrite,cssmin",
    output="css/create_edit_event.min.css",
)
css_detail_organization = Bundle(
    scss_detail_organization,
    filters="cssrewrite,cssmin",
    output="css/detail_organization.min.css",
)


# JS minify
js_base = Bundle(
    "js/lib/sticky_polyfill.js",
    filters="jsmin",
    output="js/sticky_polyfill.min.js",
)
js_places = Bundle(
    "js/lib/leaflet.js",
    "js/places/leaflet_custom.js",
    "js/places/custom.js",
    filters="jsmin",
    output="js/places/places.min.js",
)
js_create_edit_place = Bundle(
    "js/lib/auto-complete.js",
    "js/places/create_edit.js",
    "js/lib/gov_addresses.js",
    filters="jsmin",
    output="js/places/create_edit.min.js",
)
js_create_edit_user = Bundle(
    "js/lib/auto-complete.js",
    "js/user/create_edit.js",
    "js/lib/gov_addresses.js",
    filters="jsmin",
    output="js/user/create_edit.min.js",
)
js_detail_place = Bundle(
    "js/lib/leaflet.js",
    "js/places/leaflet_custom.js",
    "js/places/detail.js",
    filters="jsmin",
    output="js/places/detail_place.min.js",
)
js_detail_event = Bundle(
    "js/lib/leaflet.js",
    "js/events/detail_event.js",
    "js/lib/auto-complete.js",
    "js/user/create_edit.js",
    "js/lib/gov_addresses.js",
    "js/user/autocomplete.js",
    filters="jsmin",
    output="js/events/detail_event.min.js",
)
js_create_edit_event = Bundle(
    "js/lib/flatpickr.js",
    "js/events/create_edit_event.js",
    filters="jsmin",
    output="js/events/create_edit_event.min.js",
)
js_recurrent_event = Bundle(
    "js/events/recurrent_event.js",
    filters="jsmin",
    output="js/events/recurrent_event.min.js",
)
js_detail_organization = Bundle(
    "js/lib/auto-complete.js",
    "js/user/create_edit.js",
    "js/lib/gov_addresses.js",
    "js/user/autocomplete.js",
    filters="jsmin",
    output="js/user/detail_organization.min.js",
)
js_groups_organization = Bundle(
    "js/lib/auto-complete.js",
    "js/user/create_edit.js",
    "js/lib/gov_addresses.js",
    "js/user/autocomplete.js",
    filters="jsmin",
    output="js/user/groups_organization.min.js",
)
js_create_stuff = Bundle(
    "js/inventory/create_stuff.js",
    filters="jsmin",
    output="js/inventory/create_stuff.min.js"
)
js_edit_owner_stuff = Bundle(
    "js/inventory/edit_owner_stuff.js",
    filters="jsmin",
    output="js/inventory/edit_owner_stuff.min.js"
)
js_waypoints = Bundle(
    "js/lib/jquery.waypoints.js", filters="jsmin", output="js/user/waypoints.min.js"
)
js_infinite = Bundle(
    "js/lib/infinite.min.js", filters="jsmin", output="js/user/infinite.min.js"
)

register("css_custom_bootstrap", css_custom_bootstrap)
register("css_openrepairplatform", css_openrepairplatform)
register("css_places", css_places)
register("css_autocomplete", css_auto_complete)
register("css_detail_place", css_detail_place)
register("css_detail_event", css_detail_event)
register("css_detail_user", css_detail_user)
register("css_create_edit_event", css_create_edit_event)
register("css_detail_organization", css_detail_organization)

register("js_base", js_base)
register("js_places", js_places)
register("js_create_edit_place", js_create_edit_place)
register("js_create_edit_user", js_create_edit_user)
register("js_detail_place", js_detail_place)
register("js_detail_event", js_detail_event)
register("js_create_edit_event", js_create_edit_event)
register("js_recurrent_event", js_recurrent_event)
register("js_detail_organization", js_detail_organization)
register("js_groups_organization", js_groups_organization)
register("js_create_stuff", js_create_stuff)
register("js_edit_owner_stuff", js_edit_owner_stuff)
register("js_waypoints", js_waypoints)
register("js_infinite", js_infinite)
