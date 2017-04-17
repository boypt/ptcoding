var gulp = require('gulp');
var template = require('gulp-template-compile');
var concat = require('gulp-concat');
var minify = require('gulp-minify');
var sourcemaps = require('gulp-sourcemaps');

//var less = require('gulp-less');
//var postcss = require('gulp-postcss');
//var autoprefixer = require('autoprefixer');
//var cleanCSS = require('gulp-clean-css');
//var rename = require("gulp-rename");



gulp.task('default', ['js_templates'], function () {
  console.log('done');
});


gulp.task('js_templates', function () {
    gulp.src('views/templates/*.html')
        .pipe(template({
          name: function (file) {
            var name = file.relative;
            var key = name.substr(0, name.lastIndexOf("."));
            console.log(`gening ${key}`);
            return key;
          }
        }))
        .pipe(concat('js_templates.js'))
        .pipe(sourcemaps.init())
        .pipe(minify({
          mangle: false,
          ext:{
            src:'-debug.js',
            min:'.js'
          },
        }))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('public/javascripts/'));
});
