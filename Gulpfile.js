/* To begin transpiling the javascript:
1. npm install -g yarn
2. yarn install
3. gulp

If the gulp version is unsupported, run: npm install -g gulp (with sudo if possible)
*/

const gulp = require("gulp");
const babel = require("gulp-babel");
const terser = require("gulp-terser");
const rename = require("gulp-rename")

const presets = ["@babel/preset-env"];

gulp.task("main", () => {
  return gulp.src("./xpuz/app/static/interaction.js")
    .pipe(babel({ presets })) // preset-env for ES5
    .pipe(terser()) // minify
    .pipe(rename("interaction.min.js"))
    .pipe(gulp.dest("./xpuz/app/static/"));
});

gulp.task("default", gulp.series("main"));