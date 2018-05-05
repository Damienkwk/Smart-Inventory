(function(){
    
    angular.module("weightApp",[])
        .controller("mainCtrl", mainCtrl);
           

    mainCtrl.$inject = ["$http","$scope","$timeout"];
    
    function mainCtrl($http,$scope, $timeout){
        const self = this;

        self.noItems = [];
        self.input = {};
        self.emailData = {};
        self.selected = {};
        self.count = 0;
        self.isCount = false;
        self.isTaring = false;
        self.isCounting = false;
        self.emailSent = false;
        
        self.itemBtn = "btn btn-default";
        self.emailBtn = "btn btn-default";

        $http.get("/api/getList").then(function(result){
            self.noItems = result.data
        }).catch(function(error){
            console.log(error)
        })

        self.onSubmit = function(){
            $http.post("/api/setList", self.input).then(function(result){
                self.noItems = result.data
            }).catch(function(error){
                console.log(error)
            })
        };

        self.onClear = function(){

            $http.get("/api/onClear").then(function(result){
                self.noItems = result.data
            }).catch(function(error){
                console.log(error)
            })

        }

        
        self.onSelect = function(item) {
            self.selected = item;
        }

        self.emailValid = function(){
            if (self.count < 4 && self.isCount == true){
                self.emailBtn = "btn btn-success"
                return false;
            }
            else{
                self.emailBtn = "btn btn-default"
                return true;
            }
        }

        self.isValid = function(){
            if(self.input.item == undefined || self.input.item == ""){
                self.itemBtn = "btn btn-default"
                return true;
            }
            else if(self.input.code == undefined || self.input.code == ""){
                self.itemBtn = "btn btn-default"
                return true;
            }
            else{
                self.itemBtn = "btn btn-success"
                return false;
            }
        }

        self.sendEmail = function(){
            self.emailData.selectedItem = self.selected.item
            $http.post("/api/email", self.emailData).then(function(result){
                self.emailSent = true;
                self.emailData = {}
            }).catch(function(error){
                console.log(error)
            })
        }

        self.onTare = function(){
            self.isCount = false;
            self.emailSent = false;
            self.isTaring = true;
            $http.get("/api/onTare").then(function(result){
                self.isTaring = false;
                setTimeout(refresh, 1000);
            }).catch(function(error){
                console.log(error)
            })
        }

        self.onCount = function(){
            self.isCounting = true;
            self.emailSent = false;
            $http.post("/api/onCount", self.selected).then(function(result){
                self.isCount = true;
                self.count = result.data
                self.isCounting = false;
                setTimeout(refresh, 1000);
            }).catch(function(error){
                console.log(error)
            })
        }
        
        
        function refresh() {
            $http.get('/api/getData') .then(function(res) {
                self.input.weight = res.data;

                if(self.isTaring == true){
                    self.input.weight = "Taring";
                    console.log("Polling stopped")
                    return
                }
                else if(self.isCounting == true){
                    self.input.weight = "Counting";
                    console.log("Polling stopped")
                    return
                }
                else{
                    setTimeout(refresh, 1000);
                }

            }).catch(function(res) {
                self.input.weight = 'Server error';
            });
            
            
        }
        
        // initial call, or just call refresh directly
        setTimeout(refresh, 1000);
              
    }

})()