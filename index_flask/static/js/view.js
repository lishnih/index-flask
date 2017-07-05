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


  $("select.page").click( function(event) {
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
    td = $(this);
    tr = td.closest("tr");

    var offset = td.data("offset");
    if ( offset == -1 ) {
      tr.remove();
      return;
    }

    data = {
      "offset": offset,
    };

    $.ajax({
      type: "POST",
      dataType: "json",
      url: this.baseURI,
      data: data,
//    async: false,
      success: function(data) {
        append_rows(tr, data.rows);

        if ( data.filtered_rows_count > data.offset + data.limit ) {
          td.data("offset", data.offset + data.limit);
          $("#shown").text(data.offset + data.limit);
        } else {
          td.html("<i>Данные выведены полностью!</i>");
          td.data("offset", -1);
        }
      },
      error: function(xhr, error, thrown) {
        debug(thrown);
      },
    });
  } );


  $("li.flashes").click( function(event) {
    li = $(this);
    ul = li.closest("ul");

    li.remove();
    ul.remove();
  } );


  /*** FUNCTIONS ***/


  function round_to_int(i) {
    return i + 0.5 | 0;
  } // to_int


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


  function append_rows(tr, rows) {
    rows.forEach(function(entry) {
      var td = "";
      entry.forEach(function(i) {
        td += "<td>" + i + "</td>";
      });
      tr.before("<tr>" + td + "</tr>");
    });
  } // append_rows


} );
