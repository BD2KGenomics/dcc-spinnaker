// One line 'hack' to extract parameters from url
var params = _.object(_.compact(_.map(location.search.slice(1).split('&'), function(item) {  if (item) return item.split('='); })));

$('document').ready(function() {
  if ("submission" in params) {
    $.getJSON("/v0/submissions/" + params.submission, function(submission) {
      console.log(submission);
      $("body").html(JSON.stringify(submission));
    })
    .error(function() {
      $("body").html("error");
    });
  } else {
    $.getJSON("/v0/submissions", function(submissions) {
      console.log(submissions);
      $("body").html(JSON.stringify(submissions));
    })
    .error(function() { 
      $("body").html("error");
    });
  }
});
