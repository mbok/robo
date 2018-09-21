new Vue({
  el: "#console",
  data: {
    connected: false,
    control: {
      joystick: {
        v: 0.0,
        h: 0.0
      }
    }
  },
  created: function () {
    this.client = mqtt.connect("ws://localhost:9001");
    this.client.subscribe("mqtt/demo");
    this.client.on("message", this.onMessage);
    this.client.on('connect', this.onConnect);
    this.client.on('close', this.onClose);
    this.client.publish("mqtt/demo", "hello world!")
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
    }
  }
});
