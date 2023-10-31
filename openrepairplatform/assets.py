from django_assets import Bundle, register

# SCSS

scss_openrepairplatform = Bundle(
    "scss/openrepairplatform.scss",
    filters="scss",
    output="css/openrepairplatform.css",
    depends=("./scss/includes/*.scss")
)
scss_places = Bundle(
    "scss/lib/leaflet.scss",
    "scss/places/leaflet_custom.scss",
    filters="scss",
    output="css/leaflet_custom.css",
)
scss_detail_place = Bundle(
    "scss/lib/leaflet.scss",
    "scss/places/leaflet_custom.scss",
    filters="scss",
    output="css/detail_place.css",
)
scss_detail_event = Bundle(
    "scss/lib/leaflet.scss",
    filters="scss",
    output="css/detail_event.css",
)

# CSS minify

css_openrepairplatform = Bundle(
    scss_openrepairplatform,
    filters="cssrewrite,cssmin",
    output="css/openrepairplatform.min.css",
)

css_places = Bundle(
    scss_places,
    filters="cssrewrite,cssmin",
    output="css/places.min.css",
)
css_detail_place = Bundle(
    scss_detail_place,
    filters="cssrewrite,cssmin",
    output="css/detail_place.min.css",
)
css_detail_event = Bundle(
    scss_detail_event,
    filters="cssrewrite,cssmin",
    output="css/detail_event.min.css",
)


# JS minify
js_base = Bundle(
    "js/lib/sticky_polyfill.js",
    "js/lib/auto-dissmiss-alerts.js",
    "js/lib/modal.js",
    filters="jsmin",
    output="js/base.min.js",
)
js_create_stuff_autocomplete = Bundle(
    "/usr/local/lib/python3.9/site-packages/dal_select2/static/autocomplete_light/vendor/select2/dist/js/select2.full.js",
    "/usr/local/lib/python3.9/site-packages/dal_select2/static/autocomplete_light/vendor/select2/dist/css/select2.css",
    "/usr/local/lib/python3.9/site-packages/django/contrib/admin/static/admin/css/autocomplete.css",
    "/usr/local/lib/python3.9/site-packages/dal_select2/static/autocomplete_light/select2.css",
    "/usr/local/lib/python3.9/site-packages/dal/static/autocomplete_light/jquery.init.js",
    "/usr/local/lib/python3.9/site-packages/dal_select2/static/autocomplete_light/vendor/select2/dist/js/i18n/fr.js",
    "/usr/local/lib/python3.9/site-packages/dal/static/autocomplete_light/autocomplete.init.js",
    "/usr/local/lib/python3.9/site-packages/dal/static/autocomplete_light/forward.js",
    "/usr/local/lib/python3.9/site-packages/dal_select2/static/autocomplete_light/select2.js",
    "/usr/local/lib/python3.9/site-packages/dal/static/autocomplete_light/jquery.post-setup.js",  
    filters="jsmin",
    output="js/create_stuff_autocomplete.min.js",
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
    filters="jsmin",
    output="js/events/detail_event.min.js",
)
js_event_list = Bundle(
    "js/lib/jquery.waypoints.js",
    "js/lib/infinite.min.js",
    "js/events/event_list.js",
    filters="jsmin",
    output="js/events/event_list.min.js",
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
    output="js/inventory/create_stuff.min.js",
)
js_edit_owner_stuff = Bundle(
    "js/inventory/edit_owner_stuff.js",
    filters="jsmin",
    output="js/inventory/edit_owner_stuff.min.js",
)
js_waypoints = Bundle(
    "js/lib/jquery.waypoints.js", filters="jsmin", output="js/user/waypoints.min.js"
)
js_infinite = Bundle(
    "js/lib/infinite.min.js", filters="jsmin", output="js/user/infinite.min.js"
)

register("css_openrepairplatform", css_openrepairplatform)
register("css_places", css_places)
register("css_detail_place", css_detail_place)
register("css_detail_event", css_detail_event)

register("js_base", js_base)
register("js_create_stuff_autocomplete", js_create_stuff_autocomplete)
register("js_places", js_places)
register("js_create_edit_place", js_create_edit_place)
register("js_create_edit_user", js_create_edit_user)
register("js_detail_place", js_detail_place)
register("js_detail_event", js_detail_event)
register("js_event_list", js_event_list)
register("js_recurrent_event", js_recurrent_event)
register("js_detail_organization", js_detail_organization)
register("js_groups_organization", js_groups_organization)
register("js_create_stuff", js_create_stuff)
register("js_edit_owner_stuff", js_edit_owner_stuff)
register("js_waypoints", js_waypoints)
register("js_infinite", js_infinite)
