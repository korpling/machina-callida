export class Language {
    public name: string;
    public shortcut: string;
    constructor(init?: Partial<Language>) {
        Object.assign(this, init);
    }
}
