var cc = new Vue({
  el: "#console",
  data: {
    connected: false,
    control: {
      joystick: {
        v: 0.0,
        h: 0.0
      },
      speach: {
        say: ""
      }
    }
  },
  created: function () {
    this.client = mqtt.connect("ws://ameise-mint:9001");
    this.client.subscribe("mqtt/demo");
    this.client.on("message", this.onMessage);
    this.client.on('connect', this.onConnect);
    this.client.on('close', this.onClose);

    this.$on("joystick", this.onJoystick);
  },
  methods: {
    onMessage: function (topic, payload) {
      console.log([topic, payload].join(": "));
    },
    onConnect: function() {
      this.connected = true;
    },
    onClose: function() {
      this.connected = false;
    },
    publish: function(relativeTopic, payload) {
      this.client.publish("robo/" + relativeTopic, payload+"", {retain: true});
    },
    onJoystick: function({event, data}) {
      if (event.type == "move") {
        var h = - Math.round((((data.angle.degree % 180) - 90) / 90.0) * 100);
        var v = Math.min(Math.round(data.distance), 100);
        this.publish("joystick/h/ratio", h);
        this.publish("joystick/v/ratio", v);
        console.log("Joystick change: h x v: ", h, v);
      } else if (event.type == "end") {
        this.publish("joystick/h/ratio", 0);
        this.publish("joystick/v/ratio", 0);
        console.log("Joystick stop");
      }
    }
  }
});

var joystick = nipplejs.create({
    zone: document.getElementById('joystick'),
    mode: 'static',
    position: {left: '50%', top: '50%'},
    color: 'red',
    size: 200
});
joystick.on('start end pressure move', function(event, data) {
      cc.$emit("joystick", { "event": event, "data": data });
    });
