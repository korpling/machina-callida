import {Component, OnInit} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController} from '@ionic/angular';
import {HttpClient} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';
import {ExerciseDocumentation} from 'src/app/models/exerciseDocumentation';

@Component({
    selector: 'app-doc-exercises',
    templateUrl: './doc-exercises.page.html',
    styleUrls: ['./doc-exercises.page.scss'],
})

export class DocExercisesPage implements OnInit {
    exerciseGenDocs: ExerciseDocumentation[] = [];
    vocUnitDocs: ExerciseDocumentation[] = [];

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public translate: TranslateService,
                public helperService: HelperService) {
    }

    ngOnInit(): void {
        [...Array(10).keys()].forEach((i: number) => {
            this.vocUnitDocs.push(new ExerciseDocumentation({
                name: `DOC_EXERCISES_VOC_UNIT_${i + 1}`,
                function: `DOC_EXERCISES_VOC_UNIT_${i + 1}_FUNCTION`,
                level: `DOC_EXERCISES_VOC_UNIT_${i + 1}_LEVEL`,
                type: `DOC_EXERCISES_VOC_UNIT_${i + 1}_TYPE`
            }));
        });
        [...Array(3).keys()].forEach((i: number) => {
            this.exerciseGenDocs.push(new ExerciseDocumentation({
                name: `DOC_EXERCISES_GEN_${i + 1}`,
                function: `DOC_EXERCISES_GEN_${i + 1}_FUNCTION`,
                level: `DOC_EXERCISES_GEN_${i + 1}_LEVEL`,
                type: `DOC_EXERCISES_GEN_${i + 1}_TYPE`
            }));
        });
    }
}
