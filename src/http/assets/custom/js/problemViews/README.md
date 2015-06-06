### How to create a problem view?

* You first need to create a javascript file. Name it by the following convention:
  * The first letter should be uppercased
  * The extension should be '.js'
  * It should not contain any special character (alphanumeric characters only)
* In this file, create a class that has the same name as the javascript file, first letter uppercased, '.js' extension removed. The constructor should take the jquery element in which the view will be drawn.
* Implement the following functions:
  * `initialize(initData)`: initialize the view. The `initData` given are the one sent by the problem that is being solver (see: `BaseProblem.initView`)
  * `onData(data)`: do whatever you want with the data given by both the solver and the problem being solved. See: `BaseProblen.viz`
* Finally, to allow hooking up the problem view to a problem class, you need to update the file `hook.json` that contains, for each problem implementation, the list of available visualizations. The mapping is: <class name>:<javascript file path>. The path is relative to the `/assets/custom/js/problemViews` folder.
