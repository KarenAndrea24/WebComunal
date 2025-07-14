// static/js/datatable-docs.js
// -----------------------------------------------------------------------------
//  DataTables – documentos de venta (Facturas, Boletas, NC, ND)
//  Versión DRY que centraliza la lógica de tablas, filtros externos, exportación
// -----------------------------------------------------------------------------

'use strict';
/* global $, $.fn */

/**
 * Inicializa una tabla DataTables para el módulo de documentos de venta.
 * @param {Object} opts
 * @param {string} opts.urlDatos        – Endpoint JSON (Django) que devuelve {data: […]}
 * @param {string} opts.tablaSelector   – Selector CSS de la <table>
 * @param {string} opts.filtrosSelector – Selector CSS del <form> de filtros externos
 * @returns {DataTable|null}
 */
function initDocumentoTable ({ urlDatos, tablaSelector, filtrosSelector }) {
  const $tabla = $(tablaSelector);
  if (!$tabla.length) return null;

  const columnas = [
    { data: null },                      // control (responsive)
    { data: null },                      // checkbox
    { data: 'id', visible: false, searchable: false },
    { data: 'serie_documento' },
    { data: 'codigo_cliente' },
    { data: 'razon_social' },
    { data: 'moneda' },
    { data: 'serie' },
    { data: 'correlativo' },
    { data: 'condicion_pago' },
    { data: 'cuenta_asociada' },
    { data: 'referencia' },
    { data: 'fecha_contabilizacion' },
    { data: 'fecha_vencimiento' },
    { data: 'fecha_documento' },
    { data: 'tipo_documento' },
    { data: 'empleado_ventas' },
    { data: 'propietario' },
    { data: 'descuento_global' },
    { data: 'tipo_operacion' },
    { data: 'tipo_base_imponible' },
    { data: 'aplica_detraccion' },
    { data: 'aplica_auto_detraccion' },
    { data: 'concepto_detraccion' },
    { data: 'porcentaje_detraccion' },
    { data: 'base_imponible' },
    { data: 'impuesto' },
    { data: 'total_igv' },
    { data: 'monto_detraccion' },
    { data: 'operacion_detraccion' },
    { data: 'estado_fe' },
    { data: 'tipo_operacion_fe' },
    { data: 'comentarios' },
    { data: null }                       // acciones
  ];

  const dt = $tabla.DataTable({
    ajax: urlDatos,
    columns: columnas,
    columnDefs: getColumnDefs(),
    order: [[2, 'desc']],
    dom: datatableDom(),
    displayLength: 7,
    lengthMenu: [7, 10, 25, 50, 75, 100],
    language: datatableLang(),
    buttons: exportButtons(),
    responsive: responsiveCfg(),
    initComplete: () => $('.card-header').after('<hr class="my-0">')
  });

  // ------------------------------
  // Filtros externos (keyup/change)
  // ------------------------------
  const $f = $(filtrosSelector);
  $f.on('keyup change', '#filtro-serie', function () { dt.column(7).search(this.value).draw(); });
  $f.on('keyup change', '#filtro-correlativo', function () { dt.column(8).search(this.value).draw(); });
  $f.on('keyup change', '#filtro-cod', function () { dt.column(4).search(this.value).draw(); });
  $f.on('keyup change', '#filtro-razon', function () { dt.column(5).search(this.value).draw(); });
  // $f.on('click', '#limpiar-filtros', () => { $f[0].reset(); dt.columns().search('').draw(); });
  $('#limpiar-filtros').on('click', () => {
    $f[0].reset();           // vacía inputs
    dt.columns().search('').draw();
  });

  // Borrar registro (demo-only UI)
  $tabla.on('click', '.delete-record', function () {
    dt.row($(this).parents('tr')).remove().draw();
  });

  // Ajuste de tamaños por defecto (evita controles "sm")
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);

  return dt;
}

// -----------------------------------------------------------------------------
// Funciones auxiliares separadas para mantener legibilidad
// -----------------------------------------------------------------------------
function getColumnDefs () {
  return [
    {
      targets: 0,
      className: 'control',
      orderable: false,
      searchable: false,
      responsivePriority: 2,
      render: () => ''
    },
    {
      targets: 1,
      orderable: false,
      searchable: false,
      responsivePriority: 3,
      checkboxes: true,
      render: () => '<input type="checkbox" class="dt-checkboxes form-check-input">',
      checkboxes: { selectAllRender: '<input type="checkbox" class="form-check-input">' }
    },
    {
      targets: 4,
      responsivePriority: 1
    },
    {
      // Badge demo (puedes personalizar según tu status real)
      targets: -2,
      render: (data, type, full) => {
        const status = {
          1: { t: 'Current', c: 'bg-label-primary' },
          2: { t: 'Professional', c: 'bg-label-success' },
          3: { t: 'Rejected', c: 'bg-label-danger' },
          4: { t: 'Resigned', c: 'bg-label-warning' },
          5: { t: 'Applied', c: 'bg-label-info' }
        }[full.status];
        return status ? `<span class="badge ${status.c}">${status.t}</span>` : data;
      }
    },
    {
      // Acciones – placeholder (puedes enlazar a vistas/URLs reales)
      targets: -1,
      title: 'Actions',
      orderable: false,
      searchable: false,
      render: () => `
        <div class="d-inline-block">
          <a class="btn btn-sm btn-text-secondary rounded-pill btn-icon dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></a>
          <ul class="dropdown-menu dropdown-menu-end m-0">
            <li><a class="dropdown-item">Details</a></li>
            <li><a class="dropdown-item">Archive</a></li>
            <div class="dropdown-divider"></div>
            <li><a class="dropdown-item text-danger delete-record">Delete</a></li>
          </ul>
        </div>
        <a class="btn btn-sm btn-text-secondary rounded-pill btn-icon item-edit"><i class="ti ti-pencil ti-md"></i></a>`
    }
  ];
}

function datatableDom () {
  return '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-6 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end mt-n6 mt-md-0"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>';
}

function datatableLang () {
  return {
    paginate: {
      next: '<i class="ti ti-chevron-right ti-sm"></i>',
      previous: '<i class="ti ti-chevron-left ti-sm"></i>'
    }
  };
}

function exportButtons () {
  const commonExport = {
    columns: [3, 4, 5, 6, 7],
    format: { body: stripHtmlForExport }
  };

  return [
    {
      extend: 'collection',
      className: 'btn btn-label-primary dropdown-toggle me-4 waves-effect waves-light border-none',
      text: '<i class="ti ti-file-export ti-xs me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
      buttons: [
        { extend: 'print',  text: '<i class="ti ti-printer me-1"></i>Print',  className: 'dropdown-item', exportOptions: commonExport },
        { extend: 'csv',    text: '<i class="ti ti-file-text me-1"></i>Csv',   className: 'dropdown-item', exportOptions: commonExport },
        { extend: 'excel',  text: '<i class="ti ti-file-spreadsheet me-1"></i>Excel', className: 'dropdown-item', exportOptions: commonExport },
        { extend: 'pdf',    text: '<i class="ti ti-file-description me-1"></i>Pdf',  className: 'dropdown-item', exportOptions: commonExport },
        { extend: 'copy',   text: '<i class="ti ti-copy me-1"></i>Copy',  className: 'dropdown-item', exportOptions: commonExport }
      ]
    }
  ];
}

function stripHtmlForExport (inner) {
  if (!inner) return inner;
  const el = $.parseHTML(inner);
  return el.map(e => e.innerText ?? e.textContent).join('');
}

function responsiveCfg () {
  return {
    details: {
      display: $.fn.dataTable.Responsive.display.modal({
        header: row => `Details of ${row.data().razon_social || row.data().id}`
      }),
      type: 'column',
      renderer: (api, rowIdx, columns) => {
        const data = columns.map(col => col.title ? `<tr data-dt-row="${col.rowIndex}" data-dt-column="${col.columnIndex}"><td>${col.title}:</td><td>${col.data}</td></tr>` : '').join('');
        return data ? $('<table class="table"/>').append('<tbody/>').find('tbody').append(data).end() : false;
      }
    }
  };
}
