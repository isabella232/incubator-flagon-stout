  ac.registerActivityLogger( 
    "http://10.1.93.208", 
    "STOUT", 
    "v0.1"
    );

  $('#open-task-button').click(function() {
    ac.logUserActivity('User opened task form', // description
    'open_modal_tools', // activity_code
    ac.WF_CREATE // workflow State
    );
  })

  $('#task-complete-button').click(function() {
    ac.logUserActivity('User submitted task complete', // description
    'task_complete', // activity_code
    ac.OTHER // workflow State
    );
  })

  $('#hide-button').click(function() {
    ac.logUserActivity('User hid task form', // description
    'hide_modal_tools', // activity code
    ac.WF_CREATE
    );
  })