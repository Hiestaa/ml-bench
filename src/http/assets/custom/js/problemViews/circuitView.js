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
    self._initNodesPos = null;
    self._edges = null;
    self._lastBestSol = null;
    self._circuitWidth = null;
    self._circuitHeight = null;

    // to be called when the server is pushing non-initialization data
    self.onData = function (data) {
        if (!self._lastBestSol || !data.best.solution.equals(self._lastBestSol)) {
            self._lastBestSol = data.best.solution;

            var totalWidth = $(self._network.configurator.container).width();
            var totalHeight = $(self._network.configurator.container).width();
            var updates = [];

            for (var x = 0; x < self._circuitWidth; x++) {
                for (var y = 0; y < self._circuitHeight; y++) {
                    updates.push({
                        id: x + y * self._circuitWidth,
                        x: self._initNodesPos[self._circuitShuffle[self._lastBestSol[x + y * self._circuitWidth]]].x,
                        y: self._initNodesPos[self._circuitShuffle[self._lastBestSol[x + y * self._circuitWidth]]].y
                    });
                };
            };
            self._nodes.update(updates);
        }
    }

    self._saveInitNodesPos = function (totalWidth, totalHeight) {
        self._initNodesPos = {}
        // save the initial position of the nodes
        for (var x = 0; x < self._circuitWidth; x++) {
            for (var y = 0; y < self._circuitHeight; y++) {
                self._initNodesPos[x + y * self._circuitWidth] = {
                    x: x * (totalWidth - 50) / self._circuitWidth + 25,  // 25px margin on the left/right
                    y: y * (totalHeight - 50) / self._circuitHeight + 25  // 25px margin on the top/bottom
                };
            };
        };
    }

    // height is the number of components, vertically
    // width in the number of components, horizontally
    // shuffle is the shuffled array that maps a compoment index to its ideal position
    self.createGraph = function (width, height, shuffle) {
        var totalWidth = $(self._network.configurator.container).width();
        var totalHeight = $(self._network.configurator.container).width();
        self._circuitHeight = height;
        self._circuitWidth = width;
        self._circuitShuffle = shuffle;
        // create the nodes, initial state, will be moved according to the solution
        // found as the solver is running
        var toAdd = []
        for (var x = 0; x < width; x++) {
            for (var y = 0; y < height; y++) {
                toAdd.push({
                    id: self._circuitShuffle[x + y * width],
                    label: 'Component ' + (x + y * width),
                    title: 'Component ' + (x + y * width),
                    x: x * (totalWidth - 50) / width + 25,  // 25px margin on the left/right
                    y: y * (totalHeight - 50) / height + 25,  // 25px margin on the top/bottom
                    fixed: true,
                    physics: false,
                    shape: 'box'
                });
            };
        };
        self._saveInitNodesPos(totalWidth, totalHeight);
        self._nodes.add(toAdd);

        // create the edges, node (x, y) should be connected to node (x, y+1) and (x+1, y)
        toAdd = [];
        for (var x = 0; x < width; x++) {
            for (var y = 0; y < height; y++) {
                if (y < height - 1) {
                    // to left
                    toAdd.push({
                        from: x + y * width,
                        to: x + (y + 1) * width,
                        physics: false,
                        smooth: false
                    });
                }
                if (x < width - 1) {
                    // to bottom
                    toAdd.push({
                        from: x + y * width,
                        to: x + 1 + y * width,
                        physics: false,
                        smooth: false
                    });
                }
            };
        };
        self._edges.add(toAdd);
    }

    // to be called when the server is pushing initialization data
    // i.e.: data contained into a `initProblem` field.
    self.initialize = function (initData) {
        self._$visualization.html('')
            .height('400px')
            .addClass('visualization-panel');

        self._nodes = new vis.DataSet({});
        self._edges = new vis.DataSet({});
        var options = {
            clickToUse: true,
            interaction: {
                dragNodes: false
            }
        }
        self._network = new vis.Network(self._$visualization[0], {
            nodes: self._nodes,
            edges: self._edges
        }, options);

        self.createGraph(initData.width, initData.height, initData.shuffle);
    }
}
