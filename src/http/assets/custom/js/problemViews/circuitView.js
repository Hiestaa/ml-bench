// attach the .equals method to Array's prototype to call it on any array
Array.prototype.equals = function (array) {
    // if the other array is a falsy value, return
    if (!array)
        return false;

    // compare lengths - can save a lot of time
    if (this.length != array.length)
        return false;

    for (var i = 0, l=this.length; i < l; i++) {
        // Check if we have nested arrays
        if (this[i] instanceof Array && array[i] instanceof Array) {
            // recurse into the nested arrays
            if (!this[i].equals(array[i]))
                return false;
        }
        else if (this[i] != array[i]) {
            // Warning - two different object instances will never be equal: {x:20} != {x:20}
            return false;
        }
    }
    return true;
}

function CircuitView ($viewContainer) {
    var self = this;

    self._$viewContainer = $viewContainer;
    self._$visualization = self._$viewContainer.find("#problem-vis");

    self._network = null;

    self._nodes = null;
    self._edges = null;
    self._lastBestSol = null;

    // to be called when the server is pushing non-initialization data
    self.onData = function (data) {
        console.log("OnData", data);
        if (data.best.solution.length != self._nodes.length) {
            /* create the nodes, create the edges.
            Note: component 1, 1 is linked to component 1, 2 and 2, 1, etc...
            */
        }
        if (!self._lastBestSol || !data.best.solution.equals(self._lastBestSol)) {
            // move the nodes accordingly. The edges shouldn't move.
        }
        //
    }

    // height is the number of components, vertically
    // width in the number of components, horizontally
    self.createGraph = function (width, height) {
        console.log("Creating graph", width, height)
    }

    // to be called when the server is pushing initialization data
    // i.e.: data contained into a `initProblem` field.
    self.initialize = function (initData) {
        self._$visualization.html('');

        self._nodes = vis.DataSet();
        self._edges = vis.DataSet();
        var options = {
            clickToUse: true,
        }
        self._network = vis.Network(self._$visualization[0], {
            nodes: self._nodes,
            edges: self._edges
        }, options);

        self.createGraph(initData.width, initData.height);
    }
}
