export class TextRange {
    public start: string[];
    public end: string[];
    constructor(init?: Partial<TextRange>) {
        Object.assign(this, init);
    }
}
