# Views autocompletion events
from .autocomplete import (
    ConditionOrgaAutocomplete,
    FutureEventActivityAutocomplete,
    FutureEventPlaceAutocomplete,
)

# Views to manage activities
from .event_activities import (
    ActivityView,
    ActivityListView,
    ActivityFormView,
    ActivityCreateView,
    ActivityEditView,
    ActivityDeleteView,
)

# Views to manage conditions
from .event_conditions import (
    ConditionFormView,
    ConditionCreateView,
    ConditionEditView,
    ConditionDeleteView,
    ParticipationCreateView,
    ParticipationUpdateView,
    ParticipationDeleteView,
)

# Views to manage events
from .event_manager import (
    EventView,
    EventListView,
    EventFormView,
    EventEditView,
    EventCreateView,
    EventDeleteView,
    RecurrentEventCreateView,
)

# Views to manages participants and animators
from .event_participants import (
    BookView,
    AddActiveEventView,
    RemoveActiveEventView,
    CancelReservationView,
    PresentView,
    AbsentView,
)

from .event_stuff import (
    EventBookStuffView,
    StuffUserEventFormView,
    EventAddStuffView,
)


__all__ = [
    ConditionOrgaAutocomplete,
    FutureEventActivityAutocomplete,
    FutureEventPlaceAutocomplete,

    ActivityView,
    ActivityListView,
    ActivityFormView,
    ActivityCreateView,
    ActivityEditView,
    ActivityDeleteView,

    ConditionFormView,
    ConditionCreateView,
    ConditionEditView,
    ConditionDeleteView,
    ParticipationCreateView,
    ParticipationUpdateView,
    ParticipationDeleteView,

    EventView,
    EventListView,
    EventFormView,
    EventEditView,
    EventCreateView,
    EventDeleteView,
    RecurrentEventCreateView,

    BookView,
    AddActiveEventView,
    RemoveActiveEventView,
    CancelReservationView,
    PresentView,
    AbsentView,

    EventBookStuffView,
    StuffUserEventFormView,
    EventAddStuffView,
]
