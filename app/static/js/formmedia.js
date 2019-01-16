$(document).ready(function() {
       $('form').on('submit', function(event){
       	
       		event.preventDefault();
       		if(eventos == 2){

       			$.ajax({
       				eventos = 1;
       				type: "POST",
				    url: {{ url_for('formmedia', database='local')}}
				    
				    
				});

       		}
       		else{

       			$.ajax({
       				eventos = 2;
       				type: "POST",
					url: {{ url_for('formmedia', database='remota')}}
					

				});	
       		}				      		

       		
      
   		});
   	});	      