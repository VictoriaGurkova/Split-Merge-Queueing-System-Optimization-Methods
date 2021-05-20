function [g,d]=iterative_method(n,state_indices,p,q)

%    данные из примера
%    n=2; % число состояний
%    nk=[2 2]; % вектор числа управлений в состояниях
%    p(:,:,1)=[0.5 0.5; 0.8 0.2]; % вероятности для состояния 1
%    p(:,:,2)=[0.4 0.6; 0.7 0.3]; % вероятности для состояния 2
%    q(:,1)=[6;4]; % доходы для состояния 1
%    q(:,2)=[-3;-5]; % доходы для состояния 2

    nk=2; % число управлений в состояниях
    d1=[]; % начальное решение

    for i=1:length(state_indices)
        d1=[d1 1];
%        в python индексация начинается с 0, в octave с 1, приводим индексы состояний с управлением к корректным
        state_indices(i)=state_indices(i)+1;
    end

    w=0; % счетчик итераций
    flag=true; % индикатор несовпадения решений на последовательных итерациях

    % итерационный цикл
    while flag==true
        disp('Итерация ')
        w=w+1
        d=d1

        pd=[];
        qd=[];

        for i=1:n
            if in_list(i,state_indices)
                index=0;
                for j=1:length(state_indices)
                    if state_indices(j)==i
                        index=j;
                    end
                end
                pd=[pd;p(d(index),:,i)];
            else
                pd=[pd;p(1,:,i)];
            end
            qd=[qd;q(i)];
        end

        % решение системы линейных уравнений (определение весов)
        v=zeros(n,1);
        g=0;
        koef1=eye(n,n)-pd;
        koef=zeros(n,n);
        koef(:,1)=ones(n,1);
        koef(:,2:n)=koef1(:,1:n-1);
        x=koef\qd;
        g=x(1);
        v(1:n-1)=x(2:n);

        % улучшение решения
        i=1;
        while i<=n
            if in_list(i,state_indices)
                kriter=zeros(1,nk);
                for k=1:nk
                    kriter(k)=q(k)+p(k,:,i)*v;
                end
                index=0;
                for j=1:length(state_indices)
                    if state_indices(j)==i
                        index=j;
                    end
                end
                dt=find(kriter==max(kriter));
                d1(index)=dt(1);
            end
            i=i+1;
        end

        disp('Решение на итерации')
        d1

        % проверка совпадения решений на последовательных итерациях
        if all(d1==d)
            flag=false;
        end

    end % конец итерационного цикла
end

function b=in_list(i,state_indices)
    b=false;
    for index=1:length(state_indices)
        if state_indices(index)==i
            b=true;
        end
    end
end
