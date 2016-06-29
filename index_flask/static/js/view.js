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

  /* Extend table */

  $(".extendtable").click( function(event) {
    var td = $(this);
    var tr = td.closest("tr");

    var offset = td.data("offset");
    if ( offset == -1 ) {
      tr.remove();
      return;
    }

    var data = {
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
      error: function(data, content) {
        debug(content);
      },
    });
  } );


  $("li.flashes").click( function(event) {
    $(this).remove();
  } );


  /*** FUNCTIONS ***/


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
