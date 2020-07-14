import {EventMC} from './enum';

export default class EventRegistry {
    listeners: { [eventName: string]: any[] } = {};

    public off(eventName: EventMC): void {
        this.listeners[eventName] = [];
    }

    public on(eventName: EventMC, callback: any): void {
        if (!this.listeners[eventName]) {
            this.listeners[eventName] = [];
        }
        this.listeners[eventName].push(callback);
    }

    public trigger(eventName: EventMC, event: any): void {
        if (this.listeners[eventName]) {
            this.listeners[eventName].forEach(value => value(event));
        }
    }
}
