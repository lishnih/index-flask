// stan 2016-05-26


jQuery( function($) {


  /*** Startup ***/

  $(document).ready( function() {
    if (window.location.hash) {
      var hash = window.location.hash;
      window.location.hash = "";
//    apply_code(hash);
    }
  } );


  /*** Dialogs ***/

  // Common dialog
  $( "#dialog" ).dialog({
  	autoOpen: false,
  	width: 400,
  	buttons: [
  		{
  			text: "Ok",
  			click: function() {
  				$( this ).dialog( "close" );
  			}
  		},
  	],
  });


  /*** EVENTS ***/

  /* Navigation */

  $("span.navigator").click( function(event) {
    span = $(this);
    form = span.closest("form");

    Offset = $('input#offset', form);
    Limit = $('input#limit', form);
    Ffwd = $('span.ffwd', form);

    var offset = parseInt(Offset.attr('value'));
    var limit = parseInt(Limit.attr('value'));
    var filtered = parseInt(Ffwd.data('filtered'));
    var max = to_int(filtered/limit) * limit;

    if (span.hasClass('frw'))
        Offset.attr('value', 0);
    else if (span.hasClass('rew')) {
        offset -= limit;
        if (offset<0) offset = 0;
        Offset.attr('value', offset);
    } else if (span.hasClass('fwd')) {
        offset += limit;
        if (offset>max) offset = max;
        Offset.attr('value', offset);
    } else if (span.hasClass('ffwd'))
        Offset.attr('value', max);

//  doFormSubmit(form);
  } );


  $("select.page").change( function(event) {
    select = $(this);
    form = select.closest("form");

    Offset = $('input#offset', form);
    Limit = $('input#limit', form);

    var current = parseInt($("option:selected", select).val()) - 1;
    var limit = parseInt(Limit.attr('value'));

    Offset.attr('value', current * limit);

//  doFormSubmit(form);
  } );


  /* Extend table */

  $(".extendtable").click( function(event) {
    span = $(this);
    td = span.closest("td");

    get_rows(td);
  } );


  $(".show_all").click( function(event) {
    span = $(this);
    td = span.closest("td");

    get_rows(td, 'all');
  } );


  /* Remove flash */

  $("li.flashes").click( function(event) {
    li = $(this);
    ul = li.closest("ul");

    li.remove();
    ul.remove();
  } );


} );


/*** FUNCTIONS ***/


function round_to_int(i) {
  return i + 0.5 | 0;
} // round_to_int


function to_int(i) {
  return i | 0;
} // to_int


function doFormSubmit(form) {
  var url = form.attr("action");
  var formData = $(form).serializeArray();
  $.post(url, formData).done(function (data) {
      alert(data);
  });
  return true;
} // doFormSubmit


function get_rows(td, unlim) {
  if (typeof unlim == "undefined")
    var unlim = 0;

  tr = td.closest("tr");
  table = tr.closest("table");

  var offset = table.data("offset");
  var limit = table.data("limit");
  var query = table.data("query");

  data = {
    "offset": offset + limit,
    "limit": unlim ? 0 : limit,
    "query_json": $.toJSON(query),
    "format": "json",
  };

  $.ajax({
    type: "POST",
    dataType: "json",
    url: location.href,
    data: data,
//  async: false,
    success: function(data) {
      append_rows(tr, data.rows);

      if ( data.filtered > data.offset + data.shown ) {
        table.data("offset", data.offset);
        table.data("limit", data.limit);
      } else {
        table.data("offset", null);
        table.data("limit", null);
        td.html('<i>Данные выведены полностью!</i>')
          .click( function(event) {
            td = $(this);
            tr = td.closest("tr");
            tr.remove();
          } );
      };
    },
    error: function(xhr, error, thrown) {
      debug("Ошибка при получении данных json!");
    },
  });
} // get_rows


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


function save_sheet(table1) {

  var rows = [];
  $('tr', table1).each(function() {
    tr = $(this);
    row = []
    $('td', tr).each(function() {
      row.push(this.innerText);
    });
    rows.push(row);
  });

  data = {
    "db":   'xls0p3_reports_12V0304_2016',
    "name": 'default',
    "type": 'sheet',
    "input_data": $.toJSON(rows),
  };

  $.ajax({
    type: "POST",
    dataType: "json",
    url: '/user_data/',
    data: data,
//  async: false,
    success: function(data) {
      $( "#dialog #dialog_content" ).text("Data saved!");
    	$( "#dialog" ).dialog( "open" );
    },
    error: function(data, content) {
      debug(content);
    },
  });

} // save_sheet
