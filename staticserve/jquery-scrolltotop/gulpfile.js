var gulp = require ('gulp'),
	uglify = require ('gulp-uglify'),
	rename = require ('gulp-rename'),
	cssmin = require ('gulp-cssmin');

gulp.task ('compress', function ()
{
	gulp.src ('src/*.js')
		.pipe (uglify ())
		.pipe (rename ({suffix: '.min'}))
		.pipe (gulp.dest ('dist/'));

	gulp.src ('src/*.css')
		.pipe (cssmin ())
		.pipe (rename ({suffix: '.min'}))
		.pipe (gulp.dest ('dist/'));
});