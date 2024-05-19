/* To begin transpiling the javascript:
1. npm install --global yarn
2. yarn install
3. gulp
*/

const gulp = require("gulp");
const babel = require("gulp-babel");
const terser = require("gulp-terser");
const rename = require("gulp-rename")

const presets = ["@babel/preset-env"];

gulp.task("main", () => {
  return gulp.src("./crossword_puzzle/cword_webapp/static/interaction.js")
    .pipe(babel({ presets })) // preset-env for ES5
    .pipe(terser()) // minify
    .pipe(rename("interaction.min.js"))
    .pipe(gulp.dest("./crossword_puzzle/cword_webapp/static/"));
});

gulp.task("default", gulp.series("main"));