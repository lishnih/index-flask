// stan 2012-02-04


var json_url = "/j2"


// Запрашивает действие 'action' с опциями 'options'
// Полученный ответ передаёт в функцию success_callback с вызовом
function request_action(action, options, success_callback, async) {
  if (typeof async == "undefined")
    async = true;

  data_array = $.extend({action: action}, options);
  $.ajax({
    url: json_url,
    type: "POST",
    data: data_array,
    dataType: "json",
    cache: false,
    async: async,
//  beforeSend: function(xhr) {
//    xhr.setRequestHeader("Content-type", "application/json; charset=utf-8");
//  },
    success: function(event, xhr, ajaxOptions) {
      if (typeof event.debug     != "undefined")
        debug(event.debug);
      if (typeof event.info      != "undefined")
        debug(event.info);
      if (typeof event.warning   != "undefined")
        debug(event.warning);
      if (typeof event.error     != "undefined")
        debug(event.error);
      if (typeof event.exception != "undefined") {
        debug(event);
        debug(event.exception);
      }

      success_callback.call(this, event, xhr, ajaxOptions);
    }
  });
}


jQuery.fn.extend({


  // Запрашивает действие 'action' с опциями 'options'
  // Полученный ответ передаёт в функцию success_callback, возвращённое значение
  // присваивается вызываемому элементу/элементам
  put_action: function(action, options, success_callback) {
    return this.each( function() {
      var self = this;

      request_action(action, options, function(event, xhr, ajaxOptions) {
        content = success_callback.call(this, event, self);
        if (typeof content != "undefined")
          self.innerHTML = content;
      } );

    } );
  },


  put_count: function(table, filter) {
    return this.each( function() {
      var self = this;

      var filter_json = $.toJSON(filter);
      options = {tables: table, filter_json: filter_json};
      request_action('table_count', options, function(event, xhr, ajaxOptions) {
        if (typeof event.filtered_rows_count == "undefined")
          self.innerHTML = "<i>недоступно</i>";
        else
          self.innerHTML = event.filtered_rows_count;
      } );

    } );
  },


  put_column_func: function(table, column, func, filter) {
    return this.each( function() {
      var self = this;

      var filter_json = $.toJSON(filter);
      options = {tables: table, column: column, func: func, filter_json: filter_json};
      request_action('column_func', options, function(event, xhr, ajaxOptions) {
        if (typeof event.sum == "undefined")
          self.innerHTML = "<i>недоступно</i>";
        else
          self.innerHTML = event.sum;   // !!!
      } );

    } );
  },


  put_sum: function(table, column, filter) {
    return this.each( function() {
      var self = this;

      var filter_json = $.toJSON(filter);
      options = {tables: table, column: column, filter_json: filter_json};
      request_action('column_sum', options, function(event, xhr, ajaxOptions) {
        if (typeof event.sum == "undefined")
          self.innerHTML = "<i>недоступно</i>";
        else
          self.innerHTML = event.sum;
      } );

    } );
  },


  put_table: function(tables, columns, filter, sorting, append_options) {
    if (typeof tables  == "undefined")
      tables  = '';
    if (typeof columns == "undefined")
      columns = '';
    if (typeof filter  == "undefined" | !filter)
      filter  = {};
    if (typeof sorting == "undefined" | !sorting)
      sorting = [];
    if (typeof append_options == "undefined" | !append_options)
      append_options = {};

    return this.each( function() {
      self = this;

      var table_id = self.id;

      jtable = $(self);
      jtable_info = $('#' + table_id + '_info');
      jtable_debug = $('#' + table_id + '_debug');

      var filter_json  = $.toJSON(filter);
      var sorting_json = $.toJSON(sorting);
      options = {tables: tables, columns: columns,
                 filter_json: filter_json, sorting_json: sorting_json};

      if (append_options)
        options = $.extend(options, append_options)

      request_action('table_view', options, function(event, xhr, ajaxOptions) {

        jtable.text('');
        jtable_info.text('');
        jtable_debug.text('');

        if (!options['tables']) {
          jtable_info.text('Таблица не задана!');
          return;
        }
      
        var tableisempty = true;
      
        if (typeof event.columns != "undefined") {
          tableisempty = false;
          jtable.append('<thead><tr>');
          event.columns.forEach( function(val) {
            $("thead tr", self).append('<th>' + val + '</th>');
          } );
        }
      
        if (typeof event.rows != "undefined") {
          tableisempty = false;
          jtable.append('<tbody>');
          var i = 0;
          event.rows.forEach( function(tr_vals) {
            $("tbody", self).append('<tr id="tr' + i + '">');

            if (0 in tr_vals)
              tr_vals.forEach( function(val) {
                $("tbody tr#tr" + i, self).append('<td>' + val + '</td>');
              } );
            else
              event.columns.forEach( function(val) {
                $("tbody tr#tr" + i, self).append('<td>' + tr_vals[val] + '</td>');
              } );

            i++;
          } );
          update_gtb();
        }
      
        if (tableisempty) {
          jtable_info.text('Данные отсутствуют!');
          return;
        }

        jtable.tablesorter({debug: true, widgets: ['zebra']});
        jtable.click( function(event) {
          onTdClick(event, function(target) {
            target_tr = target.parentNode;
            $(target_tr).toggleClass('highlighted');
          } );
        } );
        jtable.addClass('tablesorter');

        if (event.filtered_rows_count == event.full_rows_count)
          jtable_info
            .text('Показано: {0} из {1}'
              .format(event.rows_count, event.filtered_rows_count));
        else
          jtable_info
            .text('Показано: {0} из {1} (до фильтрации: {2})'
              .format(event.rows_count, event.filtered_rows_count, event.full_rows_count));

        jtable_debug.text(event.query);

      } );

    } );
  },


  put_datatable: function(table, columns, filter, search) {
    // Если колонки не заданы - получаем их
    if (typeof columns == "undefined" | !columns) {
      columns = [];
      options = {tables: table, fullnames: 1};
      request_action('columns_list', options, function(event) {
        columns = event.rows;
      }, false);
    }

    if (typeof filter == "undefined" | !filter)
      filter = {};

    if (typeof search == "undefined")
      search = '';

    return this.each( function() {
      var self = this;
      jself = $(self);

      thead = $('thead', self);
      thead.text('');
      tfoot = $('tfoot', self);
      tfoot.text('');

      // Рисуем колонки
      head_tr = $('<tr>');
      foot_tr = $('<tr>');
      columns.forEach( function(val) {
        head_td = $('<th>').html(val.replace('.', '<br />'));
        head_tr.append(head_td);
        foot_td = $('<th>').html('<input type="text" name="search_platform" value="Поиск..." class="search_init" />');
        foot_tr.append(foot_td);
      } );

      thead.append(head_tr);
      tfoot.append(foot_tr);

      $("input", tfoot).focus( function() {
        if (this.className == "search_init") {
          this.className = "";
          this.value = "";
        }
      } );
       
      $("input", tfoot).blur( function(i) {
        if (this.value == "") {
          this.className = "search_init";
          this.value = $("input", tfoot).index(this);
        }
      } );

      // Загружаем таблицу
      oTable = jself.dataTable({
        "bJQueryUI": true,
        "sDom": '<"H"lfrip>t<"F"><"clear">T<"clear">',

        "bAutoWidth": false,
        "bDestroy": true,

        "bProcessing": true,
        "bServerSide": true,
        "sAjaxSource": json_url,

//     "bScrollInfinite": true,
//     "bScrollCollapse": true,
//     "sScrollY": "600px",
//     "iDisplayLength": 50,

//      "bStateSave": true,
        "aLengthMenu": [[10, 20, 50, 100, -1], [10, 20, 50, 100, "Все"]],
        "sPaginationType": "full_numbers",

        "oLanguage": {
            "sSearch": "Поиск"
        },

        // Передаём для обработки следующие данные
//         for(var i=0; i<objCols.length; i++) {
//             arrCols.push(objCols[i].mDataProp);
//         }
//         //endFor
//         aoData.push({ "name": "sColNames", "value": arrCols.join("|") });

        "oSearch": {
          "sSearch": search,
        },

        "fnServerParams": function(aoData) {
          var iDisplayStart  = this.fnSettings()._iDisplayStart;
          var iDisplayLength = this.fnSettings()._iDisplayLength;
//        var sSearch        = this.fnSettings()._sSearch;
//        var bRegex         = this.fnSettings()._bRegex;
//        var iColumns       = this.fnSettings()._iColumns;

          aoData.push( { "name": "action", "value": "table_view" } );
          aoData.push( { "name": "tables", "value": table } );
          aoData.push( { "name": "offset", "value": iDisplayStart } );
          aoData.push( { "name": "limit",  "value": iDisplayLength } );
//        aoData.push( { "name": "search", "value": sSearch } );
        },

        "fnServerData": function(sSource, aoData, fnCallback) {
//        debug(aoData);

          var sorting = [];
          var objSorts = this.fnSettings().aaSorting;

          for (var i = 0; i < objSorts.length; i++) {
              cur = objSorts[i]
              column_name = columns[cur[0]];
              column_dir  = cur[1];
              sorting.push([column_name, column_dir]);
          };

          var sorting_json = $.toJSON(sorting);
          aoData.push( { "name": "sorting_json", "value": sorting_json } );

//        request_action("table_view", aoData, fnCallback);
          $.ajax({
            url: sSource, 
            type: "POST",
            data: aoData, 
            dataType: 'json', 
            cache: false,
//          beforeSend: function(xhr) {
//            xhr.setRequestHeader("Content-type", "application/json; charset=utf-8");
//          },
            success: function(event, xhr, ajaxOptions) {
//            debug(event);
              fnCallback.call(this, event, xhr, ajaxOptions);
            }
          });
        }
      });
//    oTable.fnDestroy();
    } );
  },


});


function onTdClick(event, callback) {
  event = event || window.event;
  var target = event.target || event.srcElement;

  while(target != this) { // ( ** )
    if (target.tagName == 'TD') { // ( * )
       callback.call(this, target);
    }
    target = target.parentNode;
  }
}
