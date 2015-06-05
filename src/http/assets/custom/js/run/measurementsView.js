function MeasurementsView ($viewContainer) {
    var self = this;

    self._$viewContainer = $viewContainer;
    self._$visualization = self._$viewContainer.find("#measurements-vis");
    self._$toggleMeasureContainer = self._$viewContainer.find('#toggle-measure');

    self._graph = null;
    self._groups = null;
    self._dataset = null;
    self._startWindow = new Date();
    self._endWindow = new Date(self._startWindow.getTime() + 5);
    self._groupVisibility = {'__ungrouped__': true};

    self.onToggleGroup = function () {
        var group = $(this).data('group');
        console.log("Before toggle: ", self._groupVisibility)
        self._groupVisibility[group] = !self._groupVisibility[group];
        console.log("Setting visibility: ", self._groupVisibility)
        self._graph.setOptions({
            groups: {
                visibility: self._groupVisibility
            }
        });
    }

    // fit the graph to the window, leaving some space on the right
    // so that it does not get updated too often
    self._fitGraph = function (lastAdded) {
        if (lastAdded && lastAdded.x.getTime() > self._endWindow.getTime()) {
            // the end of the window will be X seconds after the last added point
            // so that we are sure it won't be updated for the next X seconds.
            self._endWindow.setSeconds(lastAdded.x.getSeconds() + 5.5);
            console.log("Fitting to: ", self._endWindow)
            self._graph.setWindow(self._startWindow, self._endWindow, {animation: true});
        }
    }

    // Called when a new measurement is performed.
    // the measurement object should at least have the `_time` property.
    // if no other field is present, this function does nothing. Otherwise,
    // a data point is added to the graph for each other property.
    // Each property's value is expected to be a number.
    self.onMeasure = function (measure) {
        var x = new Date(measure._time * 1000); // seconds to microseconds
        var toAdd = [];
        for (var property in measure) {
            if (property == '_time')
                continue;
            // retrieve corresponding group
            var group = self._groups.get(property)
            // create it if it does not exist.
            if (!group) {
                self._groups.add({
                    id: property,
                    content: property,
                    visibility: true
                });
                var btn = $('<button class="uk-button uk-button-primary uk-active" data-group="' +
                   property + '">' + property + '</button>').appendTo(self._$toggleMeasureContainer);
                btn.click(self.onToggleGroup);
                self._groupVisibility[property] = true;
            }

            toAdd.push({
                x: x, y: measure[property], group: property
            });
        }
        self._dataset.add(toAdd);
        self._fitGraph(toAdd[toAdd.length - 1]);
    }

    self.initialize = function () {
        self._$visualization.html('');
        self._$toggleMeasureContainer.html('');

        self._startWindow = new Date();
        self._endWindow = new Date(self._startWindow.getTime() + 5);
        self._fitGraph()

        self._groups = new vis.DataSet();
        self._dataset = new vis.DataSet()
        var options = {
          clickToUse: true,
          showCurrentTime: false,
          legend: true
        };
        self._graph = new vis.Graph2d(self._$visualization[0], self._dataset, self._groups, options);
    }
}
