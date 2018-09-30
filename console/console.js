const throttle = (func, limit) => {
  let lastFunc
  let lastRan
  return function() {
    const context = this
    const args = arguments
    if (!lastRan) {
      func.apply(context, args)
      lastRan = Date.now()
    } else {
      clearTimeout(lastFunc)
      lastFunc = setTimeout(function() {
        if ((Date.now() - lastRan) >= limit) {
          func.apply(context, args)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }
}

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
    this.publishThrottled = throttle(this.publish, 300);
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
      console.log("Publish to ", relativeTopic, payload);
      this.client.publish("robo/" + relativeTopic, payload+"", {retain: false});
    },
    onJoystick: function({event, data}) {
      if (event.type == "move") {
        var h = - Math.round((((data.angle.degree % 180) - 90) / 90.0) * 100);
        var v = Math.min(Math.round(data.distance), 100) * (data.angle.degree >= 0 && data.angle.degree<=180 ? -1 : 1);
        this.control.joystick.h = h;
        this.control.joystick.v = v;
        console.log("Joystick change: h x v: ", h, v);
        this.publishThrottled("joystick/hxv/ratio", this.control.joystick.h + "x" + this.control.joystick.v);
      } else if (event.type == "end") {
        this.publishThrottled("joystick/hxv/ratio", "0x0");
      }
    }
  }
});

var joystick = nipplejs.create({
    zone: document.getElementById('joystick'),
    mode: 'static',
    position: {left: '50%', top: '50%'},
    color: 'red',
    size: 200,
    threshold: 0.7
});
joystick.on('start end pressure move', function(event, data) {
      cc.$emit("joystick", { "event": event, "data": data });
    });
