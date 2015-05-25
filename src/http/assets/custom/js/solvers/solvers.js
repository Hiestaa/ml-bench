
var default_event = function () {
    console.log("Default event fired with arguments:", arguments);
}
/*
Creates a new solver item and appends it the the given list container.
* `$listContainer`: jquery elements to which solver items should be appended
* `data`: data related to this solver, expected to contain all the fields described in the solver service.
* `events`: (optional) an object containing events that can be listened on this solver item. This includes:
    * `click`:function(solverData) fired when the solver item is clicked.
    * `del`:function(solverData) fired when the solver item is deleted.
*/
function SolverItem ($listContainer, data, events) {
    var self = this;

    self._$listContainer = $listContainer
    self._template = '\
<tr><td class="clickable-list-item" data-solver-id="{{_id}}" id="{{id}}">\
    {{name}}\
    <button class="uk-button uk-button-danger uk-button-small remove-item"><i class="uk-icon-minus-circle"></i></button>\
</td></tr>';
    self._data = data;

    self._$item = $(render(self._template, data)).appendTo(self._$listContainer);

    if (!events)
        events = {}
    self._events = {
        click: events.click || default_event,
        del: events.del || default_event
    }

    self._$item.find('.remove-item').mouseover(function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        return false;
    })
    self._$item.find('.remove-item').click(function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        self._events.del(self._data)
        return false;
    })
    self._$item.click(function () {
        self._events.click(self._data);
    })
}

/*
Creates a new solver list in the given container.
The solver list will fetch all exsting solvers when initialized.
* `$container`: the jquery element container in which to display the list
* `events`: (optional) an object containing events that can be listened on this solver list. This includes:
    * `solverClick`:function(solverData) fired when a solver is clicked
    * `solverDel`:function(solverData) fired when a solver is removed
*/
function SolversList ($container, events) {
    var self = this;

    self._$container = $container;
    self._items = [];

    if (!events)
        events = {}
    self._events = {
        solverClick: events.solverClick || default_event,
        solverDel: events.solverDel || default_event
    }

    self.initialize = function () {
        self._items.length = 0;
        self._$container.html('');

        $.ajax({
            url: '/api/solvers/list',
            dataType: 'json',
            success: function (results) {
                for (var i = 0; i < results.length; i++) {
                    self._items.push( new SolverItem(
                        self._$container, results[i], {
                            click: self._events.solverClick,
                            del: self._events.solverDel
                        }));
                };
            },
            error: function (error) {
                console.error(error);
                $.UIkit.notify("An error occurred while retrieving the list of solvers, see logs for details", {status:'danger'})
            }
        });
    }
}

/*
Creates the panel able to perform CRUD operations on the solvers collection.
* `$listContainer` is the jquery element in which the list of solvers will be displayed
* `$formContainer` is the jquery element in which the solver form can be found
*/
function SolversCRUDPanel ($listContainer, $formContainer) {
    var self = this;

    self._$listContainer = $listContainer;
    self._$formContainer = $formContainer;

    self.initialize = function () {
        self._solverList.initialize();
        self._solverForm.initialize();
    }

    self.onSolverClick = function (solverData) {
        self._$listContainer.find('.clickable-list-item').removeClass('active');
        self._$listContainer.find('#' + solverData._id).addClass('active');
        self._solverForm.setSolver(solverData);
    }
    self.onSolverDelete = function (solverData) {
        $.ajax({
            url: '/api/solvers/byId',
            type: 'delete',
            dataType: 'json',
            data: {
                _id: solverData._id
            },
            success: function () {
                self._solverForm.onClear();
                self._solverList.initialize();
            },
            error: function () {
                $.UIkit.notify("An error occurred while deleting this solver. See logs for details.");
            }
        })
    }
    self.onSolverSaved = function (solverData) {
        self._solverList.initialize();
    }

    self._solverList = new SolversList(self._$listContainer, {
        solverClick: self.onSolverClick,
        solverDel: self.onSolverDelete
    });
    self._solverForm = new SolverForm(self._$formContainer, {
        saved: self.onSolverSaved
    });
}
