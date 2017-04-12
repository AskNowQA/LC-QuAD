<!DOCTYPE html>
<html>
<head>
  <!-- Standard Meta -->
  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
  <script src="static/prettyprint.js"></script>
  <!-- Site Properties -->
  <title>Question Time</title>
  <link rel="stylesheet" type="text/css" href="static/semantic.min.css">
  <style type="text/css">
  body {
    background-color: #DADADA;
  }
   body > .grid {
      height: 100%;
    }
  .ui.menu .item img.logo {
    margin-right: 1.5em;
  }
  .main.container {
    margin-top: 7em;
  }
  .wireframe {
    margin-top: 2em;
  }
  .ui.footer.segment {
    margin: 5em 0em 0em;
    padding: 5em 0em;
  }
  </style>
</head>
<body>
  <div class="middle aligned center aligned grid"">
    <div class= "column">
      <form class="ui form" method="post">
        <div class="ui text container segment">
          <p>{{verbalized_question}}</p>
        </div>
        <div class="field">
          <label>Correct Question</label>
          <input name="corrected_answer" placeholder={{verbalized_question}} type="text">
        </div>
        <button class="ui button" type="submit" formaction="/submitQuestion">Submit</button>
        <button class="ui button" type="submit" formaction="/deleteQuestion" >Delete</button>
      </form>
    <div class = "column">
      <div class="ui segment" id = "clickme">
        <pre id="json_content" hidden>{{json_content}}</pre>
        <break>
        <span id="json_opener">Click to show JSON</span>
    </div>
    </div>   
  </div>
    <script type="text/javascript" >
    $("#clickme").click(function() {
       $("#json_content").removeAttr("hidden");
       $("#json_opener").attr("hidden","pointless");
     });
  </script>
</body>

</html>
