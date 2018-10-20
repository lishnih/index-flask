// stan 2016-05-26


function round_to_int(i) {
  return i + 0.5 | 0;
} // round_to_int


function to_int(i) {
  return i | 0;
} // to_int


function set_url_param(url, key, value) {
    var url = new URL(url);
    url.searchParams.set(key, value);
    return url.href;
} // set_param


var utility = {
    escapeQuotes: function(string) {
      return string.replace(/"/g, '\\"');
    },
    unescapeQuotes: function(string) {
      return string.replace(/\\"/g, '"');
    }
};


function doFormSubmit(form) {
  var url = form.attr("action");
  var formData = $(form).serializeArray();
  $.post(url, formData).done(function (data) {
    alert(data);
  });
  return true;
} // doFormSubmit


function append_rows(tr, rows) {
  rows.forEach(function(entry) {
    var td = "<td></td>";
    entry.forEach(function(i) {
      if ( i == null )
        td += '<td><i class="inactive">null<i></td>';
      else
        td += "<td>" + i + "</td>";
    });
    tr.before("<tr>" + td + "</tr>");
  });
} // append_rows


function show_info(text, event) {
  $('#modal_title').html('<span class="fa fa-info-circle"></span> Info');
  $('#modal_message').text(text);
  $('#InfoModal').modal('toggle');

  if (typeof event != "undefined" && event)
    event.preventDefault();
} // show_info


function show_error(text, event, debug) {
  $('#modal_title').html('<span class="fa fa-warning"></span> Error');
  $('#modal_message').text(text);
  $('#modal_debug').text(debug);
  $('#InfoModal').modal('toggle');

  if (typeof event != "undefined" && event)
    event.preventDefault();
} // show_error
