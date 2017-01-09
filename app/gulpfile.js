var gulp = require('gulp');
var less = require('gulp-less');
var uglify = require('gulp-uglify');
var pkg = require('./package.json');

gulp.task('less', function() {
    return gulp.src('static/src/*.less')
        .pipe(less())
        .pipe(gulp.dest('static/compiled'))
        .pipe(browserSync.reload({
            stream: true
        }))
});
