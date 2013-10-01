
/*jslint undef: true, newcap: true, nomen: true, white: true, regexp: true */
/*jslint plusplus: true, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document */
/*globals setTimeout clearTimeout setInterval */
/*globals jQuery Slick alert confirm */


(function ($) {

    var log = function () {
        var c = window.console;
        if (c && c.log) {
            c.log(Array.prototype.slice.call(arguments));
        }
    };


    /*
     * SlickGrid's remote data manager, customized for SDI.
     * OO coding model follows SlickGrid's plugin convention.
     *
     * Usage::
     *
     *     var sdiRemoteModelPlugin = new Slick.Data.SdiRemoteModel({
     *         url: '....',
     *         sortCol: 'title',
     *         sortDir: true, // or, false for descending.
     *         extraQuery: {},
     *         minimumLoad: 100
     *     });
     *     grid.registerPlugin(sdiRemoteModelPlugin);
     *
     *     sdiRemoteModelPlugin.onDataLoaded.subscribe(function (evt, args) {
     *         ...
     *     });
     *
     *
     * When the client queries the server for data, the
     * server will receive the following query parameters:
     *
     *     from, to, sortCol, sortDir, + everything from extraQuery.
     *
     *
     * The manager will initiate a refresh query from the server, if
     *
     * - the viewport of the grid changes, and previously unloaded elements
     *   become visible for the user
     *
     * - setSorting() or setFilterArgs() are called, causing the entire cached data
     *   to be invalidated
     *
     * - an ajax response arrives to the client, and after having it processed,
     *   the viewport of the grid contains previously unloaded elements.
     *   (this is needed because any viewport change events during the
     *   active request would have been suppressed, so we have a last manual one)
     *
     *
     * The manager contains a custom ajax() method that behaves similarly to $.ajax,
     * but is also implementing a queue policy. Our current policy is that there can
     * only be 1 outgoing request at all times, and if a next request is launched then
     * the previously active request will be cancelled and its payload will
     * not be processed.
     *
     * Any actions that change the content of the grid are advised to do their
     * ajax with SdiRemoteModel.ajax(...), to allow these requests also participate
     * in the queue management. The requests will, by default, deplete all cached data
     * and add the query information that is needed to provid a refresh from
     * the server side.
     *
     */

    function SdiRemoteModel(_options) {

        // default options
        var options = {
            //url: null,         // the url of the server side search
            //sortCol: null,
            sortDir: true        // true = ascending, false = descending.
            //extraQuery: {}     // Additional parameters that will be passed to the server.
        };

        var grid;
        var data;
        var ids_to_data_key = {}; // maps row id (like "document_0") to data key
        var activeRequest;
        var scrollPosition;  // scrolling movement (prefetch) forward or backward

        // events
        var onDataLoading = new Slick.Event();
        var onDataLoaded = new Slick.Event();
        var onAjaxError = new Slick.Event();

        function init(_grid) {
            grid = _grid;
            $.extend(options, _options);

            // ajax queue management
            activeRequest = null;

            // Bind our data to the grid.
            data = {length: 0};
            grid.setData(data);

            // scrolling
            scrollPosition = -1;  // force movement forward, initially
            grid.onViewportChanged.subscribe(handleGridViewportChanged);
        }

        function destroy() {
            // Abort the request
            abortRequest();
            // (be paranoid about IE memory leaks)
            data = null;
        }

        function hasActiveRequest() {
            return activeRequest ? true : false;
        }

        function abortRequest() {
            if (hasActiveRequest()) {
                activeRequest.abort();
            }
        }

        function handleAjaxSuccess(xhr) {
            // IE seems to dump us here
            // on abort(), with data=null.
            if (xhr === null) {
                return;
            }

            activeRequest = null;

            // load the data that arrived in the payload.
            loadData(xhr);

            _invalidateRows(xhr);
            onDataLoaded.notify(xhr);

            // must re-trigger loading rows,
            // as these events were prevented during the
            // outgoing request.
            grid.onViewportChanged.notify();
        }

        function handleAjaxError(xhr, textStatus, errorThrown) {
            activeRequest = null;
            // We do not re-trigger rows, as it would cause the client
            // go into an infinite loop if there is no network to the server
            if (textStatus != 'abort') {
                // Signal the error, unless it is an abort.
                log('error: ' + textStatus);
                onAjaxError.notify({
                    xhr: xhr,
                    textStatus: textStatus,
                    errorThrown: errorThrown
                });
            }
        }

        function ajax(ajaxOpts, /*optional*/ ignoreMissing) {
            // Make an ajax request by keeping our specific queue policy

            // XXX this should be an explicit state rather than checking the dom
            if ($('.contents-error').length !== 0) {
                //console.log('prevented');
                return;
            }


            var jqXHR,
                dfd = $.Deferred(),
                promise = dfd.promise();

            // If we have an active request: always abort it.
            abortRequest();

            // add the abort method
            promise.abort = function (statusText) {
                // proxy abort to the jqXHR if it is active
                if (jqXHR) {
                    return jqXHR.abort(statusText);
                }
                // and then reject the deferred
                dfd.rejectWith(ajaxOpts.context || ajaxOpts, [promise, statusText, ""]);
                return promise;
            };

            // the request automatically gets the to, from... parameters,
            // enabling to produce a refresh together with the required action.
            if (! ignoreMissing) {
                // Clear the data that we have. We assume that the
                // request that came in, will change the data.
                _clearData();
                // Find out the data that we need to request
                var query = getMissingRowsInViewportChanged(undefined);
                // By default, we add the missing info to the query.
                ajaxOpts.data = $.extend({}, ajaxOpts.data, query);
            }
            // make the actual request
            jqXHR = $.ajax(ajaxOpts)
                .done(dfd.resolve)
                .fail(dfd.reject)
                .then(handleAjaxSuccess, handleAjaxError);

            // Remember that this request is now the active one
            activeRequest = jqXHR;
            return promise;
        }

        function handleGridViewportChanged(evt, args) {
            // This event will be ignored if we
            // have an outgoing request.
            // When the ajax arrives or gets aborted,
            // the event will be re-triggered manually.
            if (hasActiveRequest()) {
                return;
            }
            var viewportTop;
            if (args && args.scrollToTop) {
                // After a filtering, we need to scroll
                // the viewport to the top.
                viewportTop = 0;
            }
            var query = getMissingRowsInViewportChanged(viewportTop);
            ensureData(query);
        }

        function getMissingRowsInViewportChanged(viewportTop) {
            var vp = grid.getViewport(viewportTop); // if 0 is given, it scrolls up
            var top = vp.top;
            var bottom = vp.bottom;
            var direction = top >= scrollPosition ? +1 : -1;
            var query = findMissingData(top, bottom, direction);
            scrollPosition = top;
            return query;
        }

        function resetData() {
            //console.log('starting');
            abortRequest();

            var vp = grid.getViewport(null);
            var query = $.extend({
                    from: vp.top,
                    to: vp.bottom,
                    sortCol: options.sortCol || '',
                    sortDir: options.sortDir || ''
                }, (options.extraQuery || {}));
            ensureData(query);
            //console.log('finishing');
        }

        function _clearData() {
            // Delete the data
            $.each(data, function (key, value) {
                delete data[key];
            });
            // If we clear the cache: use null instead of 0, which
            // allows on-demand loading to fetch in this case, while
            // make sure not to go beyond the total, most specifically,
            // do not do any fetch _beyond_ the total.
            data.length = null;
            ids_to_data_key = {};
        }

        function clearData(/*optional*/ scrollToTop) {
             // Delete the data
            _clearData();
            abortRequest();
            // XXX updateRowCount not really needed here, since we will always
            // fetch after this, which will do the updateRowCount. Doing
            // it here though will force to loose the scroll position and move to top.
            // Similarly, we don't need to bother to invalidate the rows.
            grid.onViewportChanged.notify({scrollToTop: scrollToTop});
        }

        function loadData(_data) {
            var from = _data.from,
                to = _data.to,
                i;
            if (from !== undefined) {
                //log('loadData', from, to, to - from);
                for (i = from; i < to; i++) {
                    data[i] = _data.records[i - from];
                    if (data[i] !== undefined) {
                        ids_to_data_key[data[i].id] = i;
                    }
                }
                data.length = _data.total;
                // Update the grid.
                grid.updateRowCount();
                grid.render();
            }
        }

        function _invalidateRows(data) {
            // invalidate rows for the received data.
            if (data && data.from !== undefined) {
                var i;
                for (i = data.from; i < data.to; i++) {
                    grid.invalidateRow(i);
                }
                grid.updateRowCount();
                grid.render();
            }
        }

        function ensureData(query) {
            // abort the previous request
            abortRequest();

            if (query.from !== undefined) {   // query = {}, if there is no need to fetch

                // Prepare the options, include the query for missing data.
                var ajaxOptions = {
                    type: 'GET',
                    url: options.url,
                    data: query,
                    dataType: 'json'
                };

                // Make the ajax request. 'true' means: do not add missing data again,
                // as we have just provided it from above.
                ajax(ajaxOptions, true);

                // must trigger loaded, even if no actual data
                onDataLoading.notify({from: query.from, to: query.to});
            }
        }

        function findMissingData(from, to, direction) {
            //log('Records in viewport:', from, to, direction);

            if (from < 0) {
                throw new Error('"from" must not be negative');
            }
            if (from >= to) {
                throw new Error('"to" must be greater than "from"');
            }

            var start;
            var end;
            if (direction == +1) {
                start = from;
                end = to - 1;
            } else {
                start = to - 1;
                end = from;
            }

            // do we have all records in the viewport?
            var i = start;
            var firstMissing = null;
            var lastMissing = null;
            while (true) {
                if (! data[i]) {
                    if (firstMissing === null) {
                        firstMissing = i;
                    }
                    lastMissing = i;
                }
                if (i == end) {
                    break;
                }
                i += direction;
            }

            var total = data.length;
            if (firstMissing === null || total !== null &&
                firstMissing >= total && lastMissing >= total) {
                // We can return, nothing to fetch. One of the followings
                // has happened:
                //
                // 1. All records requested are present in the data.
                //
                // 2. The requested data is beyond the available total number
                //    of records. (We skip this check if total == null, which
                //    means that we have just cleared the cache and
                //    a full update is due.)
                //

                //log('Has already', start, end);

                return {};
            }

            start = firstMissing;
            end = lastMissing;

            //log('Missing:', firstMissing, lastMissing);

            // Load at least minimumLoad records
            if (options.minimumLoad && direction * (end - start) < options.minimumLoad) {
                end = start + direction * (options.minimumLoad - 1);
            }

            // Sort start and end now, and we can start loading.
            if (start > end) {
                from = end;
                to = start;
            } else {
                from = start;
                to = end;
            }
            if (from < 0) {
                from = 0;
            }
            // 'to' is the last item now = make it an index.
            to += 1;

            var results = $.extend({
                    from: from,
                    to: to,
                    sortCol: options.sortCol || '',
                    sortDir: options.sortDir || ''
                }, (options.extraQuery || {}));

            //log('Will load:', from, to, direction);

            return results;
        }

        function setSorting(sortCol, sortDir) {
            if (options.sortCol != sortCol || options.sortDir != sortDir) {
                options.sortCol = sortCol;
                options.sortDir = sortDir;
                // notify the grid
                clearData();
            }
        }

        function setFilterArgs(o) {
            var changed;
            $.each(o, function (key, value) {
                if (options.extraQuery[key] !== o[key]) {
                    options.extraQuery[key] = o[key];
                    changed = true;
                }
            });
            // notify the grid if any of the filters changed
            if (changed) {
                clearData(true);   // true will cause to scroll to the top.
            }
        }

        // --
        // synchronize selections, needed if sorting changed.
        // --

        function mapRowsToIds(rowArray) {
            var ids = {};
            $.each(rowArray, function (index, rowIndex) {
                var row = data[rowIndex];
                // XXX XXX Apparent problems with the global-selection checkbox. TODO
                if (row !== undefined) {
                    ids[row.id] = true;
                }
            });
            return ids;
        }

        function mapIdsToRows(ids) {
            var rows = [];
            var i;
            $.each(ids, function(key, item) {
                var data_key = ids_to_data_key[key];
                if (data[data_key] !== undefined) {
                    rows.push(data_key);
                }
            });
            return rows;
        }

        function syncGridSelection(preserveHidden) {
            var self = this;
            var selectedRowIds = mapRowsToIds(grid.getSelectedRows());
            var inHandler;

            grid.onSelectedRowsChanged.subscribe(function (e, args) {
                if (inHandler) {
                    return;
                }
                // save selections
                selectedRowIds = mapRowsToIds(grid.getSelectedRows());
                //log('saved', selectedRowIds);
            });

            onDataLoaded.subscribe(function (evt, args) {
                if (args.from !== undefined) {
                    // restore selections
                    inHandler = true;
                    var selectedRows = mapIdsToRows(selectedRowIds);
                    if (! preserveHidden) {
                        selectedRowIds = mapRowsToIds(selectedRows);
                    }
                    grid.setSelectedRows(selectedRows);
                    inHandler = false;
                }
            });
        }


        // Things we offer as public.
        return {
            // properties
            data: data,
            grid: grid,
            options: options,

            // methods
            init: init,
            destroy: destroy,

            clearData: clearData,
            loadData: loadData,
            resetData: resetData,
            setSorting: setSorting,
            setFilterArgs: setFilterArgs,
            syncGridSelection: syncGridSelection,
            ajax: ajax,
            hasActiveRequest: hasActiveRequest,

            // events
            onDataLoading: onDataLoading,
            onDataLoaded: onDataLoaded,
            onAjaxError: onAjaxError
        };
    }

    // Slick.Data.SdiRemoteModel
    $.extend(true, window, {Slick: {Data: {SdiRemoteModel: SdiRemoteModel}}});

})(jQuery);
