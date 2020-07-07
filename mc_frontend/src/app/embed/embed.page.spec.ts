import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {EmbedPage} from './embed.page';
import {ActivatedRoute} from '@angular/router';
import {of} from 'rxjs';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import Spy = jasmine.Spy;
import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';

describe('EmbedPage', () => {
    let embedPage: EmbedPage;
    let fixture: ComponentFixture<EmbedPage>;
    let loadExerciseSpy: Spy;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [EmbedPage],
            imports: [
                HttpClientModule,
                IonicStorageModule.forRoot(),
                TranslateTestingModule,
            ],
            providers: [
                {provide: ActivatedRoute, useValue: {queryParams: of({})}}
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        }).compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(EmbedPage);
        embedPage = fixture.componentInstance;
        loadExerciseSpy = spyOn(embedPage, 'loadExercise').and.returnValue(Promise.resolve());
        fixture.detectChanges();
    });

    it('should create', (done) => {
        expect(embedPage).toBeTruthy();
        loadExerciseSpy.and.callFake(() => Promise.reject());
        embedPage.ngOnInit().then(() => {
        }, () => {
            done();
        });
    });

    it('should load an exercise', (done) => {
        loadExerciseSpy.and.callThrough();
        const loadH5Pspy: Spy = spyOn(embedPage.exerciseService, 'loadH5P').and.returnValue(Promise.resolve());
        embedPage.loadExercise().then(() => {
            loadH5Pspy.and.callFake(() => Promise.reject());
            embedPage.loadExercise().then(() => {}, () => {
                expect(loadH5Pspy).toHaveBeenCalledTimes(2);
                done();
            });
        });
    });
});
