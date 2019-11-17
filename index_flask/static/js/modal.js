// stan 2018-10-12


$('.interactive').on('show.bs.modal', function (e) {
  var modal = $(this);
  var a = e.relatedTarget;
  if ( a != null ) {
    var url = new URL(a.href);
    url.searchParams.set('format', 'modal');

    this.dataset.reload_after_close = a.dataset.reload_after_close ? a.dataset.reload_after_close : '';

    modal
      .addClass('modal-scrollfix')
      .find('.modal-body')
      .html('loading...')
      .load(url.href, function() {
        init_form(modal, url);

        // Use Bootstrap's built-in function to fix scrolling (to no avail)
        modal
          .removeClass('modal-scrollfix')
          .modal('handleUpdate');
      });
  } // if
});


$('.interactive').on('hide.bs.modal', function() {
  var reload_after_close = this.dataset.reload_after_close;
  var needtoreload = $(this).hasClass('needtoreload');

  if ( reload_after_close && needtoreload ) {
    if ( reload_after_close == 'location' )
      location.reload();

    else {
      var table = $('table#table1').DataTable();
      table.draw();
    } // if
  } // if
});


function init_form(modal, url) {
  if (typeof url == "undefined")
    var url = location.href;

  var form = modal.find('form');
  form.attr('action', url);
  form.submit(submit_form);
} // function


function submit_form(e) {
  e.preventDefault();   // prevent default action

  var form = $(e.target);
  var url = form.attr('action');
  var formData = form.serialize();
  $.post(url, formData).done(function (data) {
    var modal = form.parents('.modal');
    modal
      .addClass('needtoreload')
      .find('.modal-body')
      .html(data);

    init_form(modal, url);

    modal
      .modal('handleUpdate');
  });
} // function
