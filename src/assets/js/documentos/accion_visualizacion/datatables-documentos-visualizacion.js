'use strict';
$(function () {
  $('#tabla-documentos-visualizacion').DataTable({
    paging     : true,
    searching  : true,
    info       : false,
    ordering   : true,
    displayLength: 5,
    lengthMenu: [5, 10, 25, 50],
    scrollX    : true,
    autoWidth  : false,
    language   : datatableLang(),
  });
});

function datatableLang () {
  return {
    paginate: {
      next: '<i class="ti ti-chevron-right ti-sm"></i>',
      previous: '<i class="ti ti-chevron-left ti-sm"></i>'
    }
  };
}