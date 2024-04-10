// $(function () {

//     $("#btnSubmit").click(function () {
//         const processor = $('input[name="processor"]:checked').val() || undefined;
//         const memory = $('input[name="memory"]:checked').val() || undefined;
//         const storage = $('input[name="storage"]:checked').val() || undefined;
//         const powerAdapter = $('input[name="powerAdapter"]:checked').val() || undefined;
//         const keyBoard = $('select[name="keyBoard"]').val() || undefined;
//         const finalCutPro = $('input[id="finalCutPro"]').is(':checked') || undefined;
//         const logicPro = $('#logicPro').is(':checked') || undefined;
//         const color = $('input[name="color"]:checked').val();
//         console.log($('#productForm').serialize());
//     })

//     $('#productForm').change(function () {
//         let values = {};
//         $.each($(this)[0].elements, function (i, field) {
//             if (field.type === 'checkbox' || values[field.name]) return;
//             values[field.name] = ($(field).is(':checked') || $(field).prop("tagName").toLowerCase() === 'select') && field.value;
//         });
//         $("#btnSubmit").prop("disabled", Object.values(values).some(t => !t));
//     })
//     $("#btnSubmit").prop("disabled", true);

//     $("input[name='processor']").click(function () {
//         $("input[name='processor'] + label").removeClass('active');
//         $(this)[0]?.labels[0]?.classList.add('active');
//     });

//     $("input[name='memory']").click(function () {
//         $("input[name='memory'] + label").removeClass('active');
//         $(this)[0]?.labels[0]?.classList.add('active');
//     });

//     $("input[name='storage']").click(function () {
//         $("input[name='storage'] + label").removeClass('active');
//         $(this)[0]?.labels[0]?.classList.add('active');
//     });

//     $("input[name='color']").click(function () {
//         $("input[name='color'] + label").removeClass('active');
//         $(this)[0]?.labels[0]?.classList.add('active');
//     });

//     $("input[name='powerAdapter']").click(function () {
//         $("input[name='powerAdapter'] + label").removeClass('active');
//         $(this)[0]?.labels[0]?.classList.add('active');
//     });
// });

