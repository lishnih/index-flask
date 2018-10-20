// stan 2016-05-26


jQuery( function($) {


  /*** Startup ***/

  $( document ).ready( function() {
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

  $( "span.navigator" ).click( function(event) {
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


  $( "select.page" ).change( function(event) {
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

  $( ".extendtable" ).click( function(event) {
    span = $(this);
    td = span.closest("td");

    get_rows(td);
  } );


  $( ".show_all" ).click( function(event) {
    span = $(this);
    td = span.closest("td");

    get_rows(td, 'all');
  } );


  /* Remove flash */

  $( "li.flashes" ).click( function(event) {
    li = $(this);
    ul = li.closest("ul");

    li.remove();
    ul.remove();
  } );


  /* Show hidden text */

  $( "span.hidden_text" ).click( function(event) {
    show_info(utility.unescapeQuotes(this.title), event);
  } );


  /* Interaction */

  $("span.interactive").click( function(event) {
    span = $(this);

    $.ajax({
      type: "POST",
      dataType: "json",
      url: this.baseURI,
      data: span.data(),
      success: function(data) {
        if (data.result == 'error')
          show_info(data.message);
      },
      error: function(data) {
        debug(data.responseText);
        show_info("Some server issues on request!<br />\n{0}".format(data.statusText));
      },
    });
  } );


  $("span.ia_delete").click( function(event) {
    span = $(this);
    data = span.data();

    options = {
      type: "POST",
      dataType: "json",
      url: this.baseURI,
      data: data,
      success: function(data) {
        if (data.result == 'error')
          show_info(data.message);
        else {
          tr = span.closest("tr");
          tr.remove();
        }
      },
      error: function(data) {
        debug(data.responseText);
        show_info("Some server issues on request!<br />\n{0}".format(data.statusText));
      },
    };

    $.ajax(options);
  } );


  $("span.ia_delete_conf").click( function(event) {
    span = $(this);
    data = span.data();

    options = {
      type: "POST",
      dataType: "json",
      url: this.baseURI,
      data: data,
      success: function(data) {
        if (data.result == 'error')
          show_info(data.message);
        else {
          tr = span.closest("tr");
          tr.remove();
        }
      },
      error: function(data) {
        debug(data.responseText);
        show_info("Some server issues on request!<br />\n{0}".format(data.statusText));
      },
    };


    $( "#custom_dialog" ).dialog({
      autoOpen: false,
      width: 400,
      buttons: [
        {
          text: "Ok",
          click: function() {
            $( this ).dialog( "close" );
            $.ajax(options);
          }
        },
        {
          text: "Cancel",
          click: function() {
            $( this ).dialog( "close" );
          }
        },
      ],
    });

    text = "Are you sure?"
    $( "#custom_dialog #dialog_content" ).html(text);
    $( "#custom_dialog" ).dialog("open");
    event.preventDefault();
  } );


} );


/*** FUNCTIONS ***/


function round_to_int(i) {
  return i + 0.5 | 0;
} // round_to_int


function to_int(i) {
  return i | 0;
} // to_int


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


function get_rows(td, unlim) {
  if (typeof unlim == "undefined")
    var unlim = 0;

  tr = td.closest("tr");
  table = tr.closest("table");

  var offset = table.data("offset");
  var limit = table.data("limit");
  var query = table.data("query");

  data = {
    'offset': offset + limit,
    'limit':  unlim ? 0 : limit,
    'format': 'json',
    'query_json': $.toJSON(query),
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


function show_info(text, event) {
  $( "#dialog #dialog_content" ).html(text);
  $( "#dialog" ).attr( "title", "info" );
  $( "#dialog" ).dialog( "open" );

  if (typeof event != "undefined")
    event.preventDefault();
} // show_info


function show_error(text, event) {
  $( "#dialog #dialog_content" ).html(text);
  $( "#dialog" ).attr( "title", "error" );
  $( "#dialog" ).dialog( "open" );

  if (typeof event != "undefined")
    event.preventDefault();
} // show_error


/*** user_data.js ***/

var user_data_url = '/user_data/'


function ud_request(data, f1, f2) {
  if (typeof f1 == "undefined")
    f1 = null;
  if (typeof f2 == "undefined")
    f2 = null;

  $.ajax({
    type: "POST",
    dataType: "json",
    url: user_data_url,
    data: data,
//  async: false,
    success: function(data) {
      if (data.result == 'error') {
        show_info(data.message);
        if (f2)
          f2(data);
      } else
        if (f1)
          f1(data);
    },
    error: function(data) {
      debug(data.responseText);
      show_info("Some server issues on request!<br />\n{0}".format(data.statusText));
      if (f2)
        f2();
    },
  });
} // ud_request


function udr_dbs_list(f1, f2) {
  data = {
    'action': 'dbs_list',
  };

  ud_request(data, f1, f2);
} // udr_dbs_list


function udr_names_list(db, type, f1, f2) {
  data = {
    'action': 'names_list',
    'db':     db,
    'type':   type,
  };

  ud_request(data, f1, f2)
} // udr_names_list


function udr_save(db, type, name, rows, mode, f1, f2) {
  data = {
    'action': 'save',
    'db':     db,
    'type':   type,
    'name':   name,
    'mode':   mode,
    'data_json': $.toJSON(rows),
  };

  ud_request(data, f1, f2)
} // udr_save


function ud_save_sheet(db, name, table1, mode, f1, f2) {
  var rows = [];
  $("tr", table1).each(function() {
    tr = $(this);
    var row = [];
    $("td", tr).each(function() {
      row.push(this.innerText);
    });
    rows.push(row);
  });

  udr_save(db, 'sheet', name, rows, mode, f1, f2);
} // ud_save_sheet
