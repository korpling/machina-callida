export class Citation {
    public isNumeric: boolean;
    public label: string;
    public level: string;
    public subcitations: { [value: number]: Citation; };
    public value: number;
    constructor(init?: Partial<Citation>) {
        Object.assign(this, init);
    }
}

