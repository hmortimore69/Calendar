document.addEventListener('DOMContentLoaded', function() {
    function customDayHeaderFormat(date) {
        const day = date.getDate();
        const suffix = (day % 10 === 1 && day !== 11) ? 'st' :
                       (day % 10 === 2 && day !== 12) ? 'nd' :
                       (day % 10 === 3 && day !== 13) ? 'rd' : 'th';
        return date.toLocaleDateString('en-US', { weekday: 'long' }) + ' ' + day + suffix;
    }

    function pickEventColor(calendar) {
        Swal.fire({
            title: 'Pick Event Color',
            html: '<input type="color" id="colorPicker" value="#3788d8" title="Choose event color">',
            showCancelButton: true,
            confirmButtonText: 'Apply',
            preConfirm: () => {
                const color = document.getElementById('colorPicker').value;
                document.documentElement.style.setProperty('--event-bg-color', color);
                calendar.getEvents().forEach(event => {
                    event.setProp('color', color);
                });
            }
        });
    }

    function importCalendar() {
        Swal.fire({
            title: 'Import Calendar',
            input: 'url',
            inputLabel: 'Enter the URL of the ICS file',
            inputPlaceholder: 'https://example.com/calendar.ics',
            showCancelButton: true,
            confirmButtonText: 'Import',
            showLoaderOnConfirm: true,
            preConfirm: (url) => {
                return fetch('/import_calendar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: url })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.ok) {
                        location.reload();
                    }
                })
                .catch(error => {
                    Swal.showValidationMessage(`Request failed: ${error}`);
                });
            },
            allowOutsideClick: () => !Swal.isLoading()
        });
    }

    function eventClick(info) {
        Swal.fire({
            title: info.event.title,
            html: `<b>Start:</b> ${info.event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}<br>
                   <b>End:</b> ${info.event.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}<br><br>
                   <b>Description:</b> ${info.event.extendedProps.description}`,
            icon: 'info'
        });
    }

    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        events: '/events',
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        },
        nowIndicator: true,
        dayMaxEventRows: true,
        firstDay: 1,
        fixedWeekCount: false,
        headerToolbar: {
            left: 'prev,next today importCalendar colorEvents',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay',
        },
        customButtons: {
            colorEvents: {
                text: 'Theme',
                click: function() {
                    pickEventColor(calendar);
                }
            },
            importCalendar: {
                text: 'Import',
                click: importCalendar
            }
        },
        buttonText: {
            today: 'Today',
            month: 'Month',
            week: 'Week',
            day: 'Day'
        },
        views: {
            timeGridWeek: {
                allDaySlot: true
            }
        },
        eventClick: eventClick,
        dayHeaderContent: function(arg) {
            return customDayHeaderFormat(arg.date);
        }
    });
    calendar.render();
});