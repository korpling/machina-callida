export class ExerciseDocumentation {
    public name: string;
    public type: string;
    public level: string;
    public function: string;

    constructor(init?: Partial<ExerciseDocumentation>) {
        Object.assign(this, init);
    }
}
