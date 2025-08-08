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
    columns: [
      { width: "40px" },
      { width: "96px" },
      { width: "200px" },
      { width: "70px" },
      { width: "80px" },
      { width: "90px" },
      { width: "90px" },
      { width: "90px" },
      { width: "100px" },
      { width: "80px" }, 
      { width: "120px" },
      { width: "120px" },
      { width: "100px" },
      { width: "100px" },
      { width: "100px" },  
      { width: "130px" },
      { width: "90px" },  
    ],
    language   : datatableLang(),
  });
});

// Modal ajuste
$('#docModal').on('shown.bs.modal', function () {
  $('#tabla-documentos-visualizacion').DataTable().columns.adjust();
});

// $(document).on('shown.bs.tab', 'a[data-bs-toggle="tab"]', function () {
//   tabla.columns.adjust().draw();
// });

function datatableLang () {
  return {
    paginate: {
      next: '<i class="ti ti-chevron-right ti-sm"></i>',
      previous: '<i class="ti ti-chevron-left ti-sm"></i>'
    }
  };
}