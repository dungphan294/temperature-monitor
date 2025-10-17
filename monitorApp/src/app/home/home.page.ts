import { Component, OnInit, OnDestroy } from '@angular/core';
import { IonHeader, IonToolbar, IonTitle, IonContent, IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonButton, IonSpinner } from '@ionic/angular/standalone';
import { MqttService } from '../services/mqtt.service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { ChartConfiguration } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  imports: [IonHeader, IonToolbar, IonTitle, IonContent, IonCard, IonCardHeader, IonCardTitle, IonCardContent, IonButton, IonSpinner, CommonModule, BaseChartDirective],
})
export class HomePage {
  isOn = false;
  temperature: number | null = null;
  private sub?: Subscription;
  // Keep last 30 readings
  temperatureData: number[] = [];
  labels: string[] = [];

  // Chart.js configuration
  lineChartData: ChartConfiguration<'line'>['data'] = {
    labels: this.labels,
    datasets: [
      {
        data: this.temperatureData,
        label: 'Temperature (°C)',
        fill: true,
        tension: 0.4, // smooth line
        borderColor: 'rgba(75,192,192,1)',
        backgroundColor: 'rgba(75,192,192,0.2)',
        pointRadius: 3
      }
    ]
  };

  lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    scales: {
      y: { beginAtZero: false }
    }
  };

  constructor(private mqttService: MqttService) { }

  toggleFan() {
    this.isOn = !this.isOn;
    const state = this.isOn ? 'ON' : 'OFF';
    this.mqttService.publish('pi/fan_state', state);
  }

  ngOnInit() {
    this.mqttService.connect();
    this.sub = this.mqttService.temperature$.subscribe(temp => {
      this.temperature = temp;
      if (temp !== null) {
        this.addTemperatureReading(temp);
      }
    });
  }

  ngOnDestroy() {
    this.mqttService.disconnect();
    this.sub?.unsubscribe();
  }

  addTemperatureReading(temp: number) {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString('en-GB', { hour12: false });

    this.temperatureData.push(temp);
    this.labels.push(timeLabel);

    if (this.temperatureData.length > 30) {
      this.temperatureData.shift();
      this.labels.shift();
    }

    // Update chart
    this.lineChartData = {
      ...this.lineChartData,
      labels: [...this.labels],
      datasets: [
        { ...this.lineChartData.datasets[0], data: [...this.temperatureData] }
      ]
    };
  }
}
