var OneChat = React.createClass({
  render: function() {
    var _this = this;
    var styles = {
        quoteBadge: {
            backgroundColor: 'rgba(0, 0, 0, 0.2)'
        },
        quoteBox: {
            overflow: 'hidden',
            marginTop: '-50px',
            paddingTop: '-100px',
            borderRadius: '17px',
            backgroundColor: '#5CB85C',
            marginTop: '25px',
            color:'white',
            width: '325px',
            boxShadow: '2px 2px 2px 2px #E0E0E0',
            width: '70%'
        },
        oppositeBox: {
            backgroundColor: '#4ADFCC'
        },
        quotationMark: {
            marginTop: '-10px',
            fontWeight: 'bold',
            fontSize:'100px',
            color:'white',
            fontFamily: '"Times New Roman", Georgia, Serif',
        },
        quoteText: {
            fontSize: '19px',
            marginTop: '-65px',
            color: 'black'
        },
        pullLeft: {
            float: 'left'
        },
        pullRight: {
            float: 'right'
        }
    };
    var createItem = function(item, index) {
        var mychat = false;
        if (item.u == viewData.current_user.username) {
            mychat = true;
        }
      return (
        <blockquote class="quote-box left-msg" style={[styles.quoteBox, (mychat && [styles.pullRight, styles.oppositeBox])]}>
          <p class="quotation-mark" style={[styles.quotationMark]}>
            “
          </p>
          <p class="quote-text" style={[styles.quoteText]}>
            { item.m }
          </p>
          <hr></hr>
          <div class="blog-post-actions">
            <p class="blog-post-bottom pull-left" style={ mychat ? [styles.pullRight] : [styles.pullLeft] }>
                { mychat ? 'Me' : item.u }
            </p>
            <p class="blog-post-bottom pull-right" style={ mychat ? [styles.pullLeft] : [styles.pullRight] }>
              <span class="badge quote-badge" style={[styles.badge, styles.quoteBadge]}>896</span>
            </p>
          </div>
        </blockquote>
      );
    };
    return <div>{ this.props.items.map(createItem) }</div>;
  }
});
OneChat = Radium(OneChat);

var ChatApp = React.createClass({
  mixins: [ReactFireMixin],

  getInitialState: function() {
    return {
      items: [],
      text: ''
    };
  },

  scrollElement: function() {
      //store a this ref, and
      var _this = this;
      //wait for a paint to do scrolly stuff
      window.requestAnimationFrame(function() {
          $("#auto_scroll").animate({ scrollTop: $('#auto_scroll').prop("scrollHeight")}, 1000);
      }, 0);
  },

  componentWillMount: function() {
    $.getJSON('/jwt/firebase').then(function(data) {
      var config = {
        apiKey: (data.api),
        databaseURL: "https://" + data.pid +".firebaseio.com"
      };
      firebase.initializeApp(config);
      // token auth
      firebase.auth().signInWithCustomToken(data.token).catch(function(error) {
        // Handle Errors
        var errorCode = error.code;
        var errorMessage = error.message;
        throw { 'code': errorCode, 'msg': errorMessage };
      });
      // ---- write ----
      var dbRef = firebase.database();
      var logRef = dbRef.ref('logs');
      // -- log --
      logRef.push().set(viewData.current_user);

      // ---- other components load ----
      if (enables['drawpad']) {
        $(document).ready(function() {
          var sketchpad = new Sketchpad({
            element: '#sketchpad',
            width: 300,
            height: 200,
            penSize: 10,
            color: '#FF0000'
          }, dbRef.ref(viewData.draw_ref));
          // buttons
          $( "#animate" ).click(function() {
            sketchpad.animate();
          });

          $( "#redo" ).click(function() {
            sketchpad.redo();
          });

          $( "#undo" ).click(function() {
            sketchpad.undo();
          });
        });
      };
      return dbRef.ref(viewData.chat_ref);
    }).then(function(dataRef) {
      this.bindAsArray(dataRef.limitToLast(25), 'items');
      this.dataRef = dataRef; // set visible to all components
      return true; // force wait for json
    }.bind(this));
  },

  handleSubmit: function(e) {
    e.preventDefault();
    if (this.state.text && this.state.text.trim().length !== 0) {
     this.firebaseRefs['items'].push({
       m: this.state.text,
       u: viewData.current_user.username
     });
     this.setState({
       text: ''
     });
   }
  },

  onChange: function(e) {
    this.setState({text: e.target.value});
  },

  componentWillUnmount: function() {
    this.dataRef.off();
  },

  render: function() {
    this.scrollElement();
    styles = {
      bottom: {
        position: 'absolute',
        bottom: 0,
        right: 0
      }
    };
    return (
      <div style="height:100%">
        <OneChat items={ this.state.items } />
        <form onSubmit={ this.handleSubmit } style={[styles.bottom]}>
          <input onChange={ this.onChange } value={ this.state.text } />
          <button>{ 'Chat #' + (this.state.items.length + 1) }</button>
        </form>
      </div>
    );
  }
});
ChatApp = Radium(ChatApp);

ReactDOM.render(<ChatApp />, document.getElementById('firebase_inject'));
