import { Injectable } from '@angular/core';
import mqtt, { MqttClient } from 'mqtt';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class MqttService {
    private client!: MqttClient;
    isConnected = false;
    message$ = new Subject<{ topic: string; payload: string }>();
    temperature$ = new BehaviorSubject<number | null>(null);

    connect() {
        
        this.client = mqtt.connect('ws://192.168.2.16:9001');

        this.client.on('connect', () => {
            console.log('✅ MQTT connected');
            this.client.subscribe('pi/temperature', (err) => {
                if (!err) console.log('Subscribed to pi/temperature');
            });
        });

        this.client.on('message', (topic, message) => {
            const msg = message.toString();
            if (topic === 'pi/temperature') {
                const temp = parseFloat(msg);
                console.log(`🌡️ pi/temperature: ${temp}`);
                this.temperature$.next(temp);
            }
        });


        this.client.on('message', (topic, message) => {
            const msg = message.toString();
            console.log(`📩 ${topic}: ${msg}`);
            this.message$.next({ topic, payload: msg });
        });

        this.client.on('close', () => {
            this.isConnected = false;
            console.warn('❌ MQTT disconnected');
        });

        this.client.on('error', (err) => {
            this.isConnected = false;
            console.error('MQTT error:', err);
        });
    }

    publish(topic: string, msg: string) {
        if (this.client && this.client.connected) {
            this.client.publish(topic, msg);
            console.log(`🚀 Published: ${topic} → ${msg}`);
        } else {
            console.warn('MQTT not connected yet');
        }
    }

    disconnect() {
        if (this.client) {
            this.client.end();
            this.isConnected = false;
            console.log('🔌 MQTT disconnected manually');
        }
    }
}
