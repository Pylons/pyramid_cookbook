
buster.testCase('sdi.grid.remotemodel', {

    setUp: function () {

        // make a mock grid
        this.grid = {
            setData: sinon.spy(),
            updateRowCount: sinon.spy(),
            render: sinon.spy(),
            onViewportChanged: {subscribe: sinon.spy()}
        };

        // make a mock Event
        window.Slick.Event = sinon.spy();

    },

    "can setup and teardown": function() {
        var grid = this.grid;

        var remote = new Slick.Data.SdiRemoteModel({
        });

        assert.equals(window.Slick.Event.callCount, 3);

        remote.init(grid);

        assert(grid.setData.calledWith({length: 0}));
        assert(grid.onViewportChanged.subscribe.called);

        remote.destroy();

    },

    'loadData': {

        setUp: function() {
            var grid = this.grid;

            var remote = this.remote = new Slick.Data.SdiRemoteModel({
            });
            remote.init(grid);

            var items = {
                to: 2, total: 999, from: 0,
                records: [
                    {name: "document_10", title: "Document 10 Binder 0"},
                    {name: "document_11", title: "Document 11 Binder 0"}
                ]
            };
            remote.loadData(items);
        },

        "can load items": function() {
            var grid = this.grid;
            var remote = this.remote;

            assert(grid.updateRowCount.called);
            assert(grid.render.called);
            assert(grid.setData.calledWith({
                0: { name: "document_10", title: "Document 10 Binder 0" },
                1: { name: "document_11", title: "Document 11 Binder 0" },
                length: 999
            }));

        },

        "is additive": function() {
            var grid = this.grid;
            var remote = this.remote;

            var items2 = {
                from: 40, to: 42, total: 999,
                records: [
                    {name: "document_40", title: "Document 40 Binder 0"},
                    {name: "document_41", title: "Document 41 Binder 0"}
                ]
            };
            remote.loadData(items2);

            assert(grid.setData.calledWith({
                0: { name: "document_10", title: "Document 10 Binder 0" },
                1: { name: "document_11", title: "Document 11 Binder 0" },
                40: { name: "document_40", title: "Document 40 Binder 0" },
                41: { name: "document_41", title: "Document 41 Binder 0" },
                length: 999
            }));

        },

       "last call overwrites total": function() {
            var grid = this.grid;
            var remote = this.remote;

            var items2 = {
                from: 40, to: 42, total: 100,
                records: [
                    {name: "document_40", title: "Document 40 Binder 0"},
                    {name: "document_41", title: "Document 41 Binder 0"}
                ]
            };
            remote.loadData(items2);

            assert(grid.updateRowCount.called);
            assert(grid.render.called);
            assert(grid.setData.calledWith({
                0: { name: "document_10", title: "Document 10 Binder 0" },
                1: { name: "document_11", title: "Document 11 Binder 0" },
                40: { name: "document_40", title: "Document 40 Binder 0" },
                41: { name: "document_41", title: "Document 41 Binder 0" },
                length: 100
            }));

        },
        tearDown: function() {
            this.remote.destroy();
        }

    }


});

