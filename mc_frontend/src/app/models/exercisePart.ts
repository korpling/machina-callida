export class ExercisePart {
    public durationSeconds: number;
    public exercises: string[];
    public startIndex: number;

    constructor(init?: Partial<ExercisePart>) {
        Object.assign(this, init);
    }
}
