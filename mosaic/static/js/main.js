/*
 * jQuery File Upload Plugin: Pool Image Upload with Auto-Upload & Thumbnail Gallery
 * Aligned for Blueimp, Django backend, and thumbnail previews.
 */
$(function () {
    'use strict';

    // Ensure #pool-thumbnails exists
    if (!$('#pool-thumbnails').length) {
        $('<div id="pool-thumbnails" style="margin-top:1em;"></div>').insertAfter('#fileupload');
    }

    // Helper: Only add unique IDs for uploaded images
    function addUploadedImageId(id) {
        var field = document.getElementById('uploaded_image_ids');
        if (!field) return;
        var ids = field.value.split(',').filter(Boolean);
        if (ids.indexOf(String(id)) === -1) {
            ids.push(String(id));
        }
        field.value = ids.join(',');
        if (typeof updateCreateMosaicButton === 'function') updateCreateMosaicButton();
    }

    // Blueimp File Upload setup for pool images
    $('#fileupload').fileupload({
        url: '/upload/', // Blueimp AJAX endpoint for pool images
        dataType: 'json',
        autoUpload: true,
        acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
        done: function (e, data) {
            if (data.result && data.result.files) {
                for (var i = 0; i < data.result.files.length; i++) {
                    var file = data.result.files[i];
                    // Robustly update hidden field (in case global handler fails)
                    if (file.id) {
                        addUploadedImageId(file.id);
                    }
                    // Call onUploadSuccess for compatibility with global logic
                    if (typeof onUploadSuccess === 'function') {
                        onUploadSuccess(file, data);
                    }
                    // Add thumbnail (clickable for carousel/gallery)
                    var thumbUrl = file.thumbnailUrl || file.url;
                    if (thumbUrl) {
                        var thumb = $('<a>')
                            .attr('href', thumbUrl)
                            .attr('data-gallery', '')
                            .append(
                                $('<img>')
                                    .attr('src', thumbUrl)
                                    .addClass('img-thumbnail')
                                    .css({'height': '64px', 'margin': '4px'})
                            );
                        $('#pool-thumbnails').append(thumb);
                    }
                }
            }
        }
    });

    // Blueimp cross-domain redirect support (needed if using iframe transport)
    $('#fileupload').fileupload(
        'option',
        'redirect',
        window.location.href.replace(/\/[^\/]*$/, '/cors/result.html?%s')
    );

    // Load existing pool files (refresh thumbnails on page load)
    $('#fileupload').addClass('fileupload-processing');
    $.ajax({
        url: $('#fileupload').fileupload('option', 'url'),
        dataType: 'json',
        context: $('#fileupload')[0]
    }).always(function () {
        $(this).removeClass('fileupload-processing');
    }).done(function (result) {
        $(this).fileupload('option', 'done')
            .call(this, $.Event('done'), {result: result});
    });
});
