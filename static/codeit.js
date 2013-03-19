$(document).ready(function(){
    function Org(title,data) {
        this.title = ko.observable(title);
        this.data = ko.observable(data);
    }

    function Repo(url,data) {
        this.url = ko.observable(url);
        this.data = ko.observable(data);
    }
    
    function CodeITViewModel() {
        // Data
        var self = this;
        self.orgs = ko.observableArray([]);
        self.repos = ko.observableArray([]);
        self.stats = ko.observableDictionary();
        // Operations
           
        $.getJSON("/orgs", function(allData) {
            var mappedOrgs = $.map(Object.keys(allData), function(item) {
                console.log('Org['+item+']='+allData[item]);
                return new Org(item.toString(),allData[item]);
                });
            self.orgs(mappedOrgs);
        });    
        $.getJSON("/repos", function(allData) {
            var mappedRepos = $.map(Object.keys(allData), function(item) {
                console.log('Repo['+item+']='+allData[item]);
                return new Repo(item.toString(),allData[item]);
                });
            self.repos(mappedRepos);
        });

        $.getJSON("/stats", function(allData) {
            $.map(Object.keys(allData), function(item){
                self.stats.set(item,allData[item]);
            });
        });
    }

    ko.applyBindings(new CodeITViewModel());
});
