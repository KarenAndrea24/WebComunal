// document.getElementById("btn-preview").addEventListener("click", function () {
//   const form = document.getElementById("carga-form");
//   const formData = new FormData(form);

//   fetch("{% url 'carga-masiva-preview' %}", {
//     method: "POST",
//     body: formData,
//     headers: { "X-CSRFToken": getCookie("csrftoken") }
//   })
//   .then(async res => {
//     if (!res.ok){
//       let data;
//       try {
//         data = await res.json();
//       } catch (err) {
//         throw new Error("El servidor devolvió una respuesta no válida");
//       }
//       throw new Error(data.error || "Error al cargar los archivos");
//       }
//     return res.json();
//   })
//   .then(data => {
//     console.log("Datos recibidos:", data);
//     renderTable("tablaCabecera", data.cabecera);
//     renderTable("tablaDetalle", data.detalle);
//     renderTable("tablaCuotas", data.cuotas);

//     window.previewData = data;
//     document.getElementById("btn-register").disabled = false;

//     Swal.fire({
//       icon: 'success',
//       title: 'Carga exitosa',
//       text: 'Los archivos se han cargado correctamente.',
//       timer: 3000,
//       showConfirmButton: false
//     });
//   })
//   .catch(error => {
//     Swal.fire({
//       icon: 'error',
//       title: 'Error al cargar archivos',
//       text: error.message || 'No se pudo procesar los archivos'
//     })
//   })
// });
